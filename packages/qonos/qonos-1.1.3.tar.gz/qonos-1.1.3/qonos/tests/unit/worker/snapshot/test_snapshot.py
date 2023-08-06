# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright 2013 Rackspace
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy
import datetime
import mox

from novaclient import exceptions

from qonos.common import timeutils
from qonos.common import utils
from qonos.openstack.common import uuidutils
import qonos.qonosclient.exception as qonos_ex
from qonos.tests.unit.worker import fakes
from qonos.tests import utils as test_utils
from qonos.worker.snapshot import snapshot


IMAGE_ID = '66666666-6666-6666-6666-66666666'


class TestSnapshotProcessor(test_utils.BaseTestCase):

    def setUp(self):
        super(TestSnapshotProcessor, self).setUp()
        self.job = copy.deepcopy(fakes.JOB['job'])
        self.mox = mox.Mox()

        self.nova_client = MockNovaClient()
        self.nova_client.servers = self.mox.CreateMockAnything()
        self.nova_client.rax_scheduled_images_python_novaclient_ext =\
            self.mox.CreateMockAnything()
        self.nova_client.images = self.mox.CreateMockAnything()
        self.qonos_client = self.mox.CreateMockAnything()
        self.worker = self.mox.CreateMockAnything()
        self.worker.get_qonos_client().AndReturn(self.qonos_client)
        self.snapshot_meta = {
            "org.openstack__1__created-by": "scheduled_images_service"
            }

    def tearDown(self):
        self.mox.UnsetStubs()
        super(TestSnapshotProcessor, self).tearDown()

    def _create_images_list(self, instance_id, image_count):
        images = []
        base_time = timeutils.utcnow()
        one_day = datetime.timedelta(days=1)
        for i in range(image_count):
            images.append(self._create_image(instance_id, base_time))
            base_time = base_time - one_day

        return images

    def _create_image(self, instance_id, created, image_id=None,
                      scheduled=True):
        image_id = image_id or uuidutils.generate_uuid()

        image = MockImage(image_id, created, instance_id)

        if scheduled:
            image.metadata['org.openstack__1__created_by'] =\
                'scheduled_images_service'

        return image

    def _init_qonos_client(self, schedule=None):
        if schedule:
            self.qonos_client.get_schedule(mox.IsA(str)).\
                AndReturn(schedule)
        else:
            self.qonos_client.get_schedule(mox.IsA(str)).\
                AndRaise(qonos_ex.NotFound())

    def _init_worker_mock(self, skip_metadata_update=False):
        self.worker.update_job(fakes.JOB_ID, 'PROCESSING',
                               timeout=mox.IsA(datetime.datetime),
                               error_message=None)
        if not skip_metadata_update:
            metadata = copy.copy(self.job['metadata'])
            metadata['image_id'] = IMAGE_ID
            self.worker.update_job_metadata(fakes.JOB_ID, metadata).\
                AndReturn(metadata)

        self._init_qonos_client(MockSchedule())

    def _simple_prepare_worker_mock(self, num_processing_updates=0,
                                    skip_metadata_update=False):
        self._init_worker_mock(skip_metadata_update)
        for i in range(num_processing_updates):
            self.worker.update_job(fakes.JOB_ID, 'PROCESSING', timeout=None,
                                   error_message=None)
        self.worker.update_job(fakes.JOB_ID, 'DONE', timeout=None,
                               error_message=None)

    def test_process_job_should_cancel_if_schedule_deleted(self):
        self._init_qonos_client()
        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        self.worker.update_job(fakes.JOB_ID, 'CANCELLED', timeout=None,
                               error_message=mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(self.job)

        self.mox.VerifyAll()

    def test_process_job_should_cancel_if_no_instance_id(self):
        self._init_qonos_client(schedule=MockSchedule())
        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        self.worker.update_job(fakes.JOB_ID, 'PROCESSING',
                               timeout=mox.IsA(datetime.datetime),
                               error_message=None)
        self.worker.update_job(fakes.JOB_ID, 'CANCELLED', timeout=None,
                               error_message=mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)
        del self.job['metadata']['instance_id']
        processor.process_job(self.job)

        self.mox.VerifyAll()

    def test_process_job_should_cancel_if_instance_not_found(self):
        self._init_qonos_client(schedule=MockSchedule())
        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str), mox.IsA(str),
            self.snapshot_meta).AndRaise(exceptions.NotFound("404"))
        self.worker.update_job(fakes.JOB_ID, 'PROCESSING',
                               timeout=mox.IsA(datetime.datetime),
                               error_message=None)
        self.worker.update_job(fakes.JOB_ID, 'CANCELLED', timeout=None,
                               error_message=mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)
        processor.process_job(self.job)

        self.mox.VerifyAll()

    def test_process_job_should_succeed_immediately(self):
        timeutils.set_time_override()
        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str),
            mox.IsA(str), self.snapshot_meta).AndReturn(IMAGE_ID)
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('ACTIVE'))
        mock_retention = MockRetention()
        self.nova_client.rax_scheduled_images_python_novaclient_ext.\
            get(mox.IsA(str)).AndReturn(mock_retention)
        self._simple_prepare_worker_mock()

        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        utils.generate_notification(None, 'qonos.job.run.end', mox.IsA(dict),
                                    mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(self.job)

        self.mox.VerifyAll()

    def test_process_job_should_continue_when_image_id_present(self):
        timeutils.set_time_override()
        self.job['metadata']['image_id'] = IMAGE_ID
        self.job['status'] = 'PROCESSING'
        # Note NO call to create_image is expected
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('ACTIVE'))

        mock_retention = MockRetention()
        self.nova_client.rax_scheduled_images_python_novaclient_ext.\
            get(mox.IsA(str)).AndReturn(mock_retention)

        self._simple_prepare_worker_mock(skip_metadata_update=True)

        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(self.job)

        self.mox.VerifyAll()

    def test_process_job_should_not_continue_when_in_bad_status(self):
        timeutils.set_time_override()
        self.job['metadata']['image_id'] = IMAGE_ID
        self.job['status'] = 'ERROR'

        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str),
            mox.IsA(str), self.snapshot_meta).AndReturn(IMAGE_ID)
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('ACTIVE'))

        mock_retention = MockRetention()
        self.nova_client.rax_scheduled_images_python_novaclient_ext.\
            get(mox.IsA(str)).AndReturn(mock_retention)

        self._simple_prepare_worker_mock()

        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(self.job)

        self.mox.VerifyAll()

    def test_process_job_should_succeed_after_multiple_tries(self):
        timeutils.set_time_override()
        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str),
            mox.IsA(str), self.snapshot_meta).AndReturn(IMAGE_ID)
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('QUEUED'))
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('SAVING'))
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('SAVING'))
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('ACTIVE'))
        mock_retention = MockRetention()
        self.nova_client.rax_scheduled_images_python_novaclient_ext.\
            get(mox.IsA(str)).AndReturn(mock_retention)
        self._simple_prepare_worker_mock()
        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        utils.generate_notification(None, 'qonos.job.run.end', mox.IsA(dict),
                                    mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(self.job)

        self.mox.VerifyAll()

    def test_process_job_should_update_status_only(self):
        base_time = timeutils.utcnow()
        time_seq = [
            base_time,
            base_time,
            base_time + datetime.timedelta(seconds=305),
            base_time + datetime.timedelta(seconds=605),
            base_time + datetime.timedelta(seconds=905),
            ]
        timeutils.set_time_override_seq(time_seq)

        job = copy.deepcopy(self.job)
        job['timeout'] = base_time + datetime.timedelta(minutes=60)

        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str),
            mox.IsA(str), self.snapshot_meta).AndReturn(IMAGE_ID)
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('QUEUED'))
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('SAVING'))
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('SAVING'))
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('ACTIVE'))
        mock_retention = MockRetention()
        self.nova_client.rax_scheduled_images_python_novaclient_ext.\
            get(mox.IsA(str)).AndReturn(mock_retention)
        self._simple_prepare_worker_mock(2)
        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        utils.generate_notification(None, 'qonos.job.run.end', mox.IsA(dict),
                                    mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(job)

        self.mox.VerifyAll()

    def test_process_job_should_update_status_and_timestamp(self):
        base_time = timeutils.utcnow()
        time_seq = [
            base_time,
            base_time,
            base_time + datetime.timedelta(seconds=305),
            base_time + datetime.timedelta(minutes=60, seconds=5),
            base_time + datetime.timedelta(minutes=60, seconds=305),
            ]
        timeutils.set_time_override_seq(time_seq)

        job = copy.deepcopy(self.job)
        job['timeout'] = base_time + datetime.timedelta(minutes=60)

        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str),
            mox.IsA(str), self.snapshot_meta).AndReturn(IMAGE_ID)
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('QUEUED'))
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('SAVING'))
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('SAVING'))
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('ACTIVE'))
        mock_retention = MockRetention()
        self.nova_client.rax_scheduled_images_python_novaclient_ext.\
            get(mox.IsA(str)).AndReturn(mock_retention)
        self._init_worker_mock()
        self.worker.update_job(fakes.JOB_ID, 'PROCESSING',
                               timeout=mox.IsA(datetime.datetime),
                               error_message=None)
        self.worker.update_job(fakes.JOB_ID, 'PROCESSING', timeout=None,
                               error_message=None)
        self.worker.update_job(fakes.JOB_ID, 'DONE', timeout=None,
                               error_message=None)
        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        utils.generate_notification(None, 'qonos.job.run.end', mox.IsA(dict),
                                    mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(job)

        self.mox.VerifyAll()

    def test_process_job_should_update_status_timestamp_no_retries(self):
        base_time = timeutils.utcnow()
        time_seq = [
            base_time,
            base_time,
            base_time + datetime.timedelta(minutes=5, seconds=5),
            base_time + datetime.timedelta(minutes=60, seconds=5),
            base_time + datetime.timedelta(minutes=120, seconds=5),
            base_time + datetime.timedelta(minutes=180, seconds=5),
            base_time + datetime.timedelta(minutes=240, seconds=5),
            ]
        timeutils.set_time_override_seq(time_seq)

        job = copy.deepcopy(self.job)
        job['timeout'] = base_time + datetime.timedelta(minutes=60)

        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str),
            mox.IsA(str), self.snapshot_meta).AndReturn(IMAGE_ID)
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('QUEUED'))
        self.nova_client.images.get(IMAGE_ID).MultipleTimes().AndReturn(
            MockImageStatus('SAVING'))

        self._init_worker_mock()
        self.worker.update_job(fakes.JOB_ID, 'PROCESSING',
                               timeout=mox.IsA(datetime.datetime),
                               error_message=None)
        self.worker.update_job(fakes.JOB_ID, 'PROCESSING',
                               timeout=mox.IsA(datetime.datetime),
                               error_message=None)
        self.worker.update_job(fakes.JOB_ID, 'PROCESSING',
                               timeout=mox.IsA(datetime.datetime),
                               error_message=None)
        self.worker.update_job(fakes.JOB_ID, 'TIMED_OUT', timeout=None,
                               error_message=None)
        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(job)

        self.mox.VerifyAll()

    def _do_test_process_job_should_update_image_error(self, error_status):
        base_time = timeutils.utcnow()
        time_seq = [
            base_time,
            base_time,
            base_time + datetime.timedelta(seconds=305),
            base_time + datetime.timedelta(seconds=605),
            base_time + datetime.timedelta(seconds=905),
            base_time + datetime.timedelta(seconds=1205),
            base_time + datetime.timedelta(seconds=1505),
            ]
        timeutils.set_time_override_seq(time_seq)

        job = copy.deepcopy(self.job)
        job['timeout'] = base_time + datetime.timedelta(minutes=60)

        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str),
            mox.IsA(str), self.snapshot_meta).AndReturn(IMAGE_ID)
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('QUEUED'))
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('SAVING'))
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('SAVING'))
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('SAVING'))
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            error_status)

        self._init_worker_mock()
        self.worker.update_job(fakes.JOB_ID, 'PROCESSING', timeout=None,
                               error_message=None)
        self.worker.update_job(fakes.JOB_ID, 'PROCESSING', timeout=None,
                               error_message=None)
        self.worker.update_job(fakes.JOB_ID, 'PROCESSING', timeout=None,
                               error_message=None)
        self.worker.update_job(fakes.JOB_ID, 'PROCESSING', timeout=None,
                               error_message=None)
        self.worker.update_job(fakes.JOB_ID, 'ERROR', timeout=None,
                               error_message=mox.IsA(str))

        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(job)

        self.mox.VerifyAll()

    def test_process_job_should_update_image_error(self):
        status = MockImageStatus('ERROR')
        self._do_test_process_job_should_update_image_error(status)

    def test_process_job_should_update_image_killed(self):
        status = MockImageStatus('KILLED')
        self._do_test_process_job_should_update_image_error(status)

    def test_process_job_should_update_image_deleted(self):
        status = MockImageStatus('DELETED')
        self._do_test_process_job_should_update_image_error(status)

    def test_process_job_should_update_image_pending_delete(self):
        status = MockImageStatus('PENDING_DELETE')
        self._do_test_process_job_should_update_image_error(status)

    def test_process_job_should_update_image_none(self):
        self._do_test_process_job_should_update_image_error(None)

    def test_doesnt_delete_images_less_than_retention(self):
        timeutils.set_time_override()
        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str),
            mox.IsA(str), self.snapshot_meta).AndReturn(IMAGE_ID)
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('ACTIVE'))
        mock_retention = MockRetention(3)
        self.nova_client.rax_scheduled_images_python_novaclient_ext.\
            get(mox.IsA(str)).AndReturn(mock_retention)
        mock_server = MockServer()
        image_list = self._create_images_list(mock_server.id, 3)
        self.nova_client.images.list(detailed=True).AndReturn(image_list)
        self._init_worker_mock()
        self.worker.update_job(fakes.JOB_ID, 'DONE', timeout=None,
                               error_message=None)
        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        utils.generate_notification(None, 'qonos.job.run.end', mox.IsA(dict),
                                    mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(self.job)

        self.mox.VerifyAll()

    def test_doesnt_delete_images_with_bad_retention(self):
        timeutils.set_time_override()
        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str),
            mox.IsA(str), self.snapshot_meta).AndReturn(IMAGE_ID)
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('ACTIVE'))
        mock_retention = MockRetention("gabe 1337")
        self.nova_client.rax_scheduled_images_python_novaclient_ext.\
            get(mox.IsA(str)).AndReturn(mock_retention)
        mock_server = MockServer()
        self._init_worker_mock()
        self.worker.update_job(fakes.JOB_ID, 'DONE', timeout=None,
                               error_message=None)
        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        utils.generate_notification(None, 'qonos.job.run.end', mox.IsA(dict),
                                    mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(self.job)

        self.mox.VerifyAll()

    def test_doesnt_delete_images_with_no_retention(self):
        timeutils.set_time_override()
        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str),
            mox.IsA(str), self.snapshot_meta).AndReturn(IMAGE_ID)
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('ACTIVE'))
        self.nova_client.rax_scheduled_images_python_novaclient_ext.\
            get(mox.IsA(str)).AndRaise(exceptions.NotFound('404!'))
        mock_server = MockServer(retention=None)
        self._init_worker_mock()
        self.worker.update_job(fakes.JOB_ID, 'DONE', timeout=None,
                               error_message=None)
        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        utils.generate_notification(None, 'qonos.job.run.end', mox.IsA(dict),
                                    mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(self.job)

        self.mox.VerifyAll()

    def test_doesnt_delete_images_on_retention_error(self):
        timeutils.set_time_override()
        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str),
            mox.IsA(str), self.snapshot_meta).AndReturn(IMAGE_ID)
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('ACTIVE'))
        self.nova_client.rax_scheduled_images_python_novaclient_ext.\
            get(mox.IsA(str)).AndRaise(Exception())
        mock_server = MockServer(retention=None)
        self._init_worker_mock()
        self.worker.update_job(fakes.JOB_ID, 'DONE', timeout=None,
                               error_message=None)
        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        utils.generate_notification(None, 'qonos.job.run.end', mox.IsA(dict),
                                    mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(self.job)

        self.mox.VerifyAll()

    def test_deletes_images_more_than_retention(self):
        timeutils.set_time_override()
        instance_id = self.job['metadata']['instance_id']
        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str),
            mox.IsA(str), self.snapshot_meta).AndReturn(IMAGE_ID)
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('ACTIVE'))
        mock_retention = MockRetention(3)
        self.nova_client.rax_scheduled_images_python_novaclient_ext.\
            get(mox.IsA(str)).AndReturn(mock_retention)
        mock_server = MockServer(instance_id=instance_id)
        image_list = self._create_images_list(mock_server.id, 5)
        self.nova_client.images.list(detailed=True).AndReturn(image_list)
        # The image list happens to be in descending created order
        self.nova_client.images.delete(image_list[-2].id)
        self.nova_client.images.delete(image_list[-1].id)
        self._init_worker_mock()
        self.worker.update_job(fakes.JOB_ID, 'DONE', timeout=None,
                               error_message=None)
        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        utils.generate_notification(None, 'qonos.job.run.end', mox.IsA(dict),
                                    mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)

        processor.process_job(self.job)

        self.mox.VerifyAll()

    def test_doesnt_delete_images_from_another_instance(self):
        timeutils.set_time_override()
        instance_id = self.job['metadata']['instance_id']
        self.nova_client.servers.get(mox.IsA(str)).AndReturn(MockServer())
        self.nova_client.servers.create_image(mox.IsA(str),
            mox.IsA(str), self.snapshot_meta).AndReturn(IMAGE_ID)
        self.nova_client.images.get(IMAGE_ID).AndReturn(
            MockImageStatus('ACTIVE'))
        mock_retention = MockRetention(3)
        self.nova_client.rax_scheduled_images_python_novaclient_ext.\
            get(mox.IsA(str)).AndReturn(mock_retention)
        mock_server = MockServer(instance_id=instance_id)
        image_list = self._create_images_list(mock_server.id, 5)
        to_delete = image_list[3:]
        image_list.extend(self._create_images_list(
                uuidutils.generate_uuid(), 3))
        self.nova_client.images.list(detailed=True).AndReturn(image_list)
        # The image list happens to be in descending created order
        self.nova_client.images.delete(to_delete[0].id)
        self.nova_client.images.delete(to_delete[1].id)
        self._simple_prepare_worker_mock()
        self.mox.StubOutWithMock(utils, 'generate_notification')
        utils.generate_notification(None, 'qonos.job.run.start', mox.IsA(dict),
                                    mox.IsA(str))
        utils.generate_notification(None, 'qonos.job.run.end', mox.IsA(dict),
                                    mox.IsA(str))
        self.mox.ReplayAll()

        processor = TestableSnapshotProcessor(self.nova_client)
        processor.init_processor(self.worker)
        processor.process_job(self.job)

        self.mox.VerifyAll()

    def test_generate_image_name(self):
        timeutils.set_time_override(datetime.datetime(2013, 3, 22, 22, 39, 27))
        timestamp = '1363991967'
        processor = TestableSnapshotProcessor(self.nova_client)
        image_name = processor.generate_image_name("test")
        self.assertEqual(image_name, 'Daily-test-' + timestamp)

    def test_generate_image_name_long_server_name(self):
        timeutils.set_time_override(datetime.datetime(2013, 3, 22, 22, 39, 27))
        timestamp = '1363991967'
        processor = TestableSnapshotProcessor(self.nova_client)
        fake_server_name = 'a' * 255
        expected_server_name = 'a' * (255 - len(timestamp) - len('Daily--'))
        image_name = processor.generate_image_name(fake_server_name)
        expected_image_name = 'Daily-' + expected_server_name + '-' + timestamp
        self.assertEqual(image_name, expected_image_name)


class MockNovaClient(object):
    def __init__(self):
        self.servers = None
        self.images = None


class MockSchedule(object):
    def __init__(self):
        pass


class MockImageStatus(object):
    def __init__(self, status):
        self.status = status


class MockImage(object):
    def __init__(self, image_id, created, instance_id):
        self.id = image_id
        self.created = created
        self.metadata = {
            'instance_uuid': instance_id,
            }


class MockServer(object):
    def __init__(self, instance_id=None, retention="0", name='test'):
        self.id = instance_id or uuidutils.generate_uuid()
        self.name = name


class MockRetention(object):
    def __init__(self, retention="0"):
        self.retention = retention


class TestableSnapshotProcessor(snapshot.SnapshotProcessor):
    def __init__(self, nova_client):
        super(TestableSnapshotProcessor, self).__init__()
        self.nova_client = nova_client

    def _get_nova_client(self):
        return self.nova_client

    def _get_utcnow(self):
        now = timeutils.utcnow()
        print "Returning NOW: %s" % str(now)
        return now
