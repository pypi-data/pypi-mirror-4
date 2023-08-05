# package
#coding=utf-8
import syslog,cStringIO,chardet,re,pycurl2,traceback
from urllib import urlencode
from urlparse import urlparse,urlunparse
from pydomain import get_host,get_subdomain

SCHEMAS = ['http', 'https', 'tencent', 'ftp']

class DRequests():
    def __init__(self, url=None,method=None,params=dict(),**args):
        self.method = method
        self.params = self._encode_params(params) 
        self.html = cStringIO.StringIO()
        self.cheader = cStringIO.StringIO()
        self.url = url
        if self.url.strip()[:7] != 'http://':
            if self.url.strip()[:8] != 'https://':
                self.url = 'http://' + self.url
            
        self.referer = args.get('referer','http://www.' + str(get_host(url)))
        self.useragent = args.get('useragent',"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)")
        self.header = args.get('header',['Referer:%s'%str(self.referer)])
        self.followlocation = args.get('followlocation', 1)
        self.nobody = args.get('nobody', 0)
        
        self._text = None
        self._server_ip = None
        self._headers = {}
        self._code = None
        self._download_size = None
        self.err = None 
        
        self.c = self._build_curl()
        self.c.nobody = self.nobody
        try:
            self.c.perform() 
        except:
            syslog.openlog('gongju_drequests', syslog.LOG_PID, syslog.LOG_LOCAL0)
            syslog.syslog(syslog.LOG_WARNING, str(traceback.format_exc()) + str(self.url))
            syslog.closelog()
            self.err = True

        self._content = self.html.getvalue()
    
    @property
    def headers(self):
        '响应头'
        if self._headers == {}:
            tmp = self.cheader.getvalue().split("\r\n")
            self._headers['ver'] = tmp[0]
            for t in tmp[1:]:
                
                item = t.split(':')
                if len(item) == 2: 
                    self._headers[item[0].strip().lower()] = item[1].strip() 
        return self._headers
    
    
    @property
    def ok(self):
        '''
        是否正常的响应
        '''
        return self.status_code >= 400
    
    @property
    def server_ip(self): 
        if self._server_ip is None:
            self._server_ip = self.get_ip()
        return self._server_ip
    
    def get_ip(self):
        ip = self.c.getinfo(pycurl2.PRIMARY_IP)
        return ip
    
    @property
    def status_code(self):
        '''
        响应码
        ''' 
        if not self._code:
            self._code = self.c.getinfo(pycurl2.HTTP_CODE)
        return self._code
    
    @property
    def download_size(self):
        '''
        下载字节数，可能是压缩过的
        ''' 
        if not self._download_size:
            self._download_size = self.c.getinfo(pycurl2.CONTENT_LENGTH_DOWNLOAD)
        
        '有些网站有内容，但返回的数据大小为　-1'
        if self._download_size == -1:
            self._download_size = self.c.getinfo(pycurl2.SIZE_DOWNLOAD)
        return self._download_size
    
    @property
    def body_size(self):
        '''
        下载字节数，解压缩过的
        '''
        return len(self._content)
    
    
    @property
    def full_url(self): 

        if not self.url:
            raise u'必须有地址'

        url = self.url
        # Support for unicode domain names and paths.
        scheme, netloc, path, params, query, fragment = urlparse(url)

        if not scheme:
            raise ValueError("Invalid URL %r: No schema supplied" % url)

        if not scheme in SCHEMAS:
            raise ValueError("Invalid scheme %r" % scheme)

        netloc = netloc.encode('idna').decode('utf-8')

        if not path:
            path = '/'


        if isinstance(scheme, str):
            scheme = scheme.encode('utf-8')
        if isinstance(netloc, str):
            netloc = netloc.encode('utf-8')
        if isinstance(path, str):
            try:
                path = path.encode('utf-8')
            except:
                path = path.decode('utf-8')
        if isinstance(params, str):
            params = params.encode('utf-8')
        if isinstance(query, str):
            try:
                query = query.decode('utf-8')
            except:
                query = query.decode('gb18030')
        if isinstance(fragment, str):
            fragment = fragment.encode('utf-8')

        url = (urlunparse([scheme, netloc, path, params, query, fragment]))

        if self.params:
            if urlparse(url).query:
                url = '%s&%s' % (url, self.params)
            else:
                url = '%s?%s' % (url, self.params)


        return url.encode('utf-8')
    
    @property
    def text(self): 
        '''
        编码后的正文内容
        '''
        if self._text is None:
            plist = [self.c.getinfo(pycurl2.CONTENT_TYPE)]
            self._text = self._decode(self._content, plist)
        
        return self._text
        
    def _decode(self,content,plist = None): 
        '''
        编码后的正文内容
        '''  
        def getcode(content,encoding):
            if encoding: 
                encoding = encoding.upper() 
            else:
                encoding = 'GB2312'
            if encoding in ['GB2312','GBK','ZH-CN', 'EUC-TW']: encoding = 'GB18030' 
             
            try:
                ret = content.decode(encoding,'ignore').encode('utf-8')  #str(self._content, encoding, errors='replace')
            except:
                return None 
            return ret
        
        is_retry = False 
        encoding = 'none'
        if plist and len(plist)!=0 and plist[0] and plist[0].find('=')!=-1: encoding = plist[0].split('=')[1].strip()
        if encoding.lower() == 'none': 
            p = re.compile( r'(<meta.*?[^>]*>)',re.IGNORECASE)
            vals = re.findall(p,content)
            p_content = ''.join(vals)
            content_ary = p_content.split('charset')
            if len(content_ary) > 1 : 
                content_ary = content_ary[1].replace('=','').strip()
                content_ary = content_ary.split('>')
                encoding = content_ary[0] 
                encoding = encoding.replace('"','').replace("'",'').replace('/','').strip() 
                is_retry = True
            else:
                encoding = chardet.detect(content)['encoding'] #response._detected_encoding()
                is_retry = False
        else: 
            is_retry = True
                
        if is_retry:
            if encoding.find(';')!=-1:
                content_ary = encoding.split(';') 
                encoding = content_ary[0]
            if encoding.find(' ')!=-1:
                content_ary = encoding.split(' ') 
                encoding = content_ary[0]
        '-----------------------------'
        ret = getcode(content,encoding)
        
        if is_retry and ret is None:
            encoding = chardet.detect(content)['encoding'] 
            ret = getcode(content,encoding)
        return ret

    def _build_curl(self): 
        c = pycurl2.Curl()
        c.setopt(pycurl2.URL, self.full_url) 
        c.setopt(c.SSL_VERIFYHOST,False)
        c.setopt(pycurl2.SSL_VERIFYPEER,False)
        c.setopt(pycurl2.NOSIGNAL,1) 
        c.setopt(pycurl2.ENCODING,'gzip,deflate') 
        c.setopt(pycurl2.WRITEFUNCTION, self.html.write)
        c.setopt(pycurl2.HEADERFUNCTION,self.cheader.write)
        c.setopt(pycurl2.NOPROGRESS, 1)
        c.setopt(pycurl2.USERAGENT, self.useragent)
        c.setopt(pycurl2.HTTPHEADER,self.header) 
        c.setopt(pycurl2.FOLLOWLOCATION, self.followlocation)
        c.setopt(pycurl2.MAXREDIRS, 5)
        c.setopt(pycurl2.CONNECTTIMEOUT, 10)  #链接超时时间
        c.setopt(pycurl2.TIMEOUT, 15)    #超时时间
        c.setopt(pycurl2.COOKIE,'/tmp/cookie.txt') 
        c.setopt(pycurl2.DNS_USE_GLOBAL_CACHE,1) #取消DNS缓存
        return c
    
    
    @staticmethod
    def _encode_params(data):  
        if hasattr(data, '__iter__') and not isinstance(data, str):
            data = dict(data)
        if hasattr(data, 'items'):
            result = []
            for k, vs in list(data.items()):
                for v in isinstance(vs, list) and vs or [vs]:
                    result.append((k.encode('utf-8') if isinstance(k, str) else k,
                                   v.encode('utf-8') if isinstance(v, str) else v))
            return urlencode(result, doseq=True)
        else:
            return data   

  
