import paramiko
import os


def sftp_multi_download(hostname, port, username, password, local_dir, remote_dir):
    t = paramiko.Transport((hostname, port))
    t.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    files = sftp.listdir(remote_dir)
    for f in files:
        sftp.get(os.path.join(remote_dir, f), os.path.join(local_dir, f))
    t.close()

if __name__ == '__main__':
    hostname = '192.168.1.88'
    username = 'xiongbin'
    password = '123456'
    port = 22
    local_dir = 'E:\\trial\\'
    remote_dir = '/home/xiongbin/store_feed/'
    sftp_multi_download(hostname, port, username, password, local_dir, remote_dir)