# package
#coding=utf-8
import chardet,re
import geventcurl as pycurl
from cStringIO import StringIO

class Curl:
    def __init__(self,url,**kw):
        self.url = self._get_yes_http(self._str_decode(url))
        self.args = kw 
        self._is_run = False
        self.err = None
        self._html = None
        self._code = None
        self._respip = None 
        self._headers = {}
        self._download_size = None
        self.c = None
        
    def __del__(self):
        if self.c:
            try:
                self.c.close()
            except:
                pass
            
            
    def _init(self): 
        self.body = StringIO()
        self.header = StringIO()
        c = pycurl.Curl() 
        c.setopt(pycurl.URL,self._str_decode(self.url))
        if self.url.lower().find('https://') == 0:
            c.setopt(pycurl.SSL_VERIFYHOST,False)
            c.setopt(pycurl.SSL_VERIFYPEER,False)
        c.setopt(pycurl.NOSIGNAL,1) 
        c.setopt(pycurl.NOPROGRESS, 1)
        c.setopt(pycurl.ENCODING,'gzip,deflate')
        agent = self.args.get('agent',None)
        if agent == 'no':pass
        else:
            if not agent: agent = "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)" 
            c.setopt(pycurl.USERAGENT, agent)
            
        '-----------------超时设置' 
        timeout = self.args.get('timeout',15)
        c.setopt(pycurl.TIMEOUT, timeout)    #超时时间
        c.setopt(pycurl.DNS_USE_GLOBAL_CACHE,1) 
        '-------------------'
        is_redirect = self.args.get('redirs',False)
        if is_redirect:
            c.setopt( pycurl.FOLLOWLOCATION, 1 )
            c.setopt( pycurl.MAXREDIRS, 5) 
        else:
            c.setopt( pycurl.FOLLOWLOCATION, 0)
            
        method = self.args.get('method','get').lower()
        #if method!='head':
            #c.setopt(pycurl.HEADER,0)
        c.setopt(pycurl.WRITEFUNCTION, self.body.write)
        '==================='
        if method == 'head': 
            c.setopt(pycurl.NOBODY,1)
        '无论如何都要将头部内容取回来'
        c.setopt(pycurl.HEADERFUNCTION, self.header.write)
        '================='
        #if method == 'get':
        #elif method == 'head': 
        #c.setopt(pycurl.NOBODY, 1)  
        if method == 'post':
            c.setopt(pycurl.POST,1)
            post_content = self.args.get('post_content',None)
            if post_content: c.setopt(pycurl.POSTFIELDS,post_content)
        else:
            c.setopt(pycurl.HTTPGET,1)
            
        cookie = self.args.get('cookie',None)
        if cookie:c.setopt(pycurl.COOKIE,cookie) 
        user = self.args.get('user',None)
        psw = self.args.get('psw',None)
        if user and psw:
            c.setopt(pycurl.HTTPAUTH,pycurl.HTTPAUTH_BASIC) 
            c.setopt(pycurl.USERPWD,user + ':' + psw) 
        
        self.c = c
        
    def _str_decode(self,val):
        '''
        将所有unicode转换成字符串
        '''
        if val and type(val) == unicode:
            val = val.encode('utf-8')
        return val
    
    def _get_yes_http(self,url):
        '''
        还原网址的http
        '''
        if url.find('://')==-1:
            url = 'http://' + url
        return url
    
    def run(self):
        '''
        一定要先调用这个才能有c
        ''' 
        try:
            self._init()
            self._is_run = True
            self.c.perform()
        except Exception,e:
            self.err = e
            return False
        return True
    @property
    def download_size(self):
        '''
        下载内容大小
        '''
        if self._download_size is None:self._download_size = self.c.getinfo(pycurl.SIZE_DOWNLOAD) 
        return self._download_size
    @property
    def headers(self):
        '响应头'
        if self._headers == {}:
            tmp = self.header.getvalue().split("\r\n")
            self._headers['ver'] = tmp[0]
            for t in tmp[1:]: 
                item = t.split(':')
                if len(item) == 2: 
                    self._headers[item[0].strip().lower()] = item[1].strip() 
        return self._headers
    @property
    def respip(self):
        '''
        服务器IP
        '''
        if self._respip is None:self._respip = str(self.c.getinfo(pycurl.PRIMARY_IP))
        return self._respip
    
    @property
    def code(self):
        '''
        响应码
        '''
        if self._code is None:self._code = self.c.getinfo(pycurl.HTTP_CODE)
        return self._code
    
    @property
    def html(self):
        '''
        取得正文
        '''
        if not self._is_run: raise Exception('请先运行RUN方法，再调用此属性')
        if self._html : return self._html
        self._html = self.body.getvalue()
        is_decode = self.args.get('decode',False)
        if is_decode:
            self._html = self._decode(self._html) 
        return self._html
    
    def _decode(self,content,plist = None):
        '''
        对正文进行相关编码
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
        if plist and plist.find('=')!=-1: encoding = plist.split('=')[1].strip()

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
    
    def close(self): 
        if self._is_run: self.c.close()
