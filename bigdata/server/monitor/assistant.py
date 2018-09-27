import smtplib
import email.mime.multipart
import email.mime.text
import time
from server.spider import rbmq_web_spider
import sys
from server.spider.proxy_ip_spider import check_update, init_mongo
from server.recv_cron.verical.recv_get_total_pages import get_rb_conn

class AT:

    def analyst_digikey_data_not_updated(self):
        from server.db.digikey.mongo_client import Digikey
        count = Digikey.getDigikey_not_update_count()
        print('个数:', count)
        self.send_email('2479025585@qq.com', '温馨提示[时间:%s]'%time.ctime(),
                '我滴亲哥，digikey的数据今天早上在0点前居然有这么多<b>'+\
                str(count) +'</b>没有更新，亲哥，快去看看吧，不然，老板要砍你了')

        self.send_email('376689390@qq.com', '温馨提醒[时间:%s]'%time.ctime(),
                '我滴亲哥，digikey的数据今天早上在0点前居然有这么多<b>'+\
                 str(count)+'</b>没有更新，亲哥，快去看看吧不然，老板要来找你了')

    def monitor_proxy_ip(self):
        conn = get_rb_conn()
        ch = conn.channel()
        for queue in ['proxy_ip_digikey', 'proxy_ip_verical', 
                'proxy_ip_alliedelec', 'proxy_ip_avnet']:
            ch.queue_declare(queue=queue, durable=True)

            rs = rbmq_web_spider.RBMQWebSpider()
            print('正在获取队列proxy_ip的数据')
            html = rs.get_data()
            data = rs.parse_get_data(html)
            proxy_ip_data = rs.get_proxy_ip_data(queue, data)
            pis = proxy_ip_data['messages_ready']

            if pis != '' and pis <= 15:
                print('正在发送邮件')
                self.send_email('2479025585@qq.com', '报警[%s' % queue +\
                        '时间:%s]'%time.ctime(), '只有<b>%s</b>个ip了' % pis)
                url = ''
                keyword = ''
                if queue == 'proxy_ip_digikey':
                    url = 'http://digikey.cn'
                    keyword = 'digikey'
                    
                elif queue == 'proxy_ip_verical':
                    url = 'https://verical.com'
                    keyword = 'verical'

                elif queue == 'proxy_ip_alliedelec':
                    url = 'http://www.alliedelec.com'
                    keyword = 'alliedelec'
                elif queue == 'proxy_ip_avnet':
                    url = 'https://avnet.com'
                    keyword = 'avnet'

                if url != '' and keyword != '':
                    check_update(queue, url, keyword)
            else:
                print('%s很健康' % queue)
        conn.close()
        
    def send_email(self, addr, subject, content):
        msg = email.mime.text.MIMEText(content, 'html', 'utf-8')
        msg['From'] = 'gfplk_admin@163.com'
        msg['To'] = addr
        msg['Subject'] = subject

        smtp = smtplib.SMTP()
        smtp.set_debuglevel(1)
        smtp.connect('smtp.163.com')  # 使用的发送者邮箱的那啥来着，post
        smtp.login('gfplk_admin@163.com', 'sc5201314')
        smtp.sendmail('gfplk_admin@163.com', addr, msg.as_string())
        smtp.quit()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        at = AT()
        if sys.argv[1] == 'digikey_count':
            at.analyst_digikey_data_not_updated()
        elif sys.argv[1] == 'proxy_ip_count':
            at.monitor_proxy_ip()
        elif sys.argv[1] == 'proxy_init_mongo':
            init_mongo()
    else:
        print('参数错误')

