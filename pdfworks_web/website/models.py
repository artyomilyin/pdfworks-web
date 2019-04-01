import hashlib
import os
import shutil
from django.conf import settings
from django.db import models


class RequestFiles(models.Model):
    TOOL_TYPE_CHOICES = [
        ('merge', 'merge'),
        ('split', 'split'),
    ]

    csrf_id = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)
    tool_type = models.CharField(max_length=200, choices=TOOL_TYPE_CHOICES)

    def __str__(self):
        return "%s request" % self.csrf_id

    def delete(self, output_filename=None, using=None, keep_parents=False):
        if self.uploaded_files:
            if self.tool_type == 'merge':
                dir_path = os.path.join(os.path.join(settings.BASE_DIR, 'uploads'), self.csrf_id)
                shutil.rmtree(dir_path)
                if output_filename:
                    os.remove(output_filename)
            elif self.tool_type == 'split':
                dir_path = os.path.join(os.path.join(settings.BASE_DIR, 'uploads'), self.csrf_id)
                shutil.rmtree(dir_path)
                if output_filename:
                    shutil.rmtree(output_filename)
        super(RequestFiles, self).delete(using=using, keep_parents=keep_parents)

    class Meta:
        verbose_name_plural = 'Request files'


class UploadedFile(models.Model):

    def define_upload_path(self, filename):
        if self.request_session.tool_type == 'split':
            string_to_hash = "%s_%s" % (self.request_session.csrf_id, filename)
            self.unq_dir_name = hashlib.sha1(string_to_hash.encode('utf-8')).hexdigest()
        elif self.request_session.tool_type == 'merge':
            self.unq_dir_name = self.request_session.csrf_id
        return "uploads/%s/%s" % (self.request_session.csrf_id, filename)

    request_session = models.ForeignKey(RequestFiles, on_delete=models.CASCADE, related_name='uploaded_files')
    filename = models.FileField(upload_to=define_upload_path)
    uuid = models.CharField(max_length=200, db_index=True)

    class Meta:
        ordering = ('id',)


class Statistic(models.Model):
    TOOL_TYPE_CHOICES = [
        ('merge', 'merge'),
        ('split', 'split'),
    ]

    tool_type = tool_type = models.CharField(max_length=200, choices=TOOL_TYPE_CHOICES)
    output_filename = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=16)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s from %s" % (self.output_filename, self.ip_address)
