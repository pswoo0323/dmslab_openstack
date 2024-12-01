from django.db import models

class IPRequest(models.Model):
    REQUEST_TYPES = [
        ('public_ip', 'Public IP'),
        ('vpn_ip', 'VPN IP'),]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),]

    id = models.BigAutoField(primary_key=True, verbose_name="Request ID")
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES, verbose_name="Request Type")
    ip_address = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True, verbose_name="Assigned IP Address")
    server_name = models.CharField(max_length=100, verbose_name="Associated Server Name")
    network_name = models.CharField(max_length=100, verbose_name="Network Name")
    requested_by = models.CharField(max_length=100, verbose_name="Requested By")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Request Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"{self.request_type} - {self.server_name} ({self.status})"

    class Meta:
        db_table = "ip_requests"
        verbose_name_plural = "IP Requests"
