import BaseHTTPServer as http
import cPickle as pickle
from socket import socket
import time
import httplib
import os
from threading import Thread
from collections import deque


from obitools import NucSequence

def scanServer(address, port):
    s = socket()
    print "Attempting to connect to %s on port %s." %(address, port)
    try:
        s.connect((address, port))
        print "Connected to server %s on port %s." %(address, port)
        return True
    except socket.error, e:
        print "Connecting to %s on port %s failed with the following error: %s" %(address, port, e)
        return False 

class Jobs:
    def __init__(self):
        pass
    
    def __call__(self):
        raise NotImplementedError
    
class JobResult:
    def __init__(self,job):
        self.jobid=job.jobid
        self.starttime=job.starttime
        self.result=job()
        
    
    
            
            

class OBIServHandler (http.BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        http.BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.finished=False
        
    def do_GET(self):
        if self.path=="/nextjob":
            try:
                agentid = (self.client_address[0],self.headers['OBIAgentID'])
                nextjob = self.server.jobIterator.next()
                self.server.jobid+=1
                nextjob.jobid=self.server.jobid
                nextjob.starttime=time.time()
                self.server.running[nextjob.jobid]=nextjob
                data = pickle.dumps(nextjob, protocol=0)
                self.send_head(data)
                self.wfile.write(data)

                if agentid not in self.server.agent:
                    print "Add a new agent : ",agentid
                    self.server.agent.add(agentid)
            except StopIteration:
                self.send_error(601, "No more jobs")
                print "Remove agent : ",agentid
                self.server.agent-=set([agentid])
                self.server.jobfinished=True
        else:
            self.send_error(404, "File not found : %s" % self.path)

    def do_POST(self):
        if self.path=="/result":
            print "I'm receiving results"
            datasize=int(self.headers['Content-Length'])
            data=self.rfile.read(datasize)
            data=pickle.loads(data)
            data.endtime=time.time()
            data.duration=data.endtime-data.starttime
            data.job=self.server.running[data.jobid]
            self.send_response(602, "Result received")
            self.server.results.append(data)
            del self.server.running[data.jobid]
            print data.result
        else:
            self.send_error(404, "File not found : %s" % self.path)
            
            
    def send_head(self,data):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        #path = self.translate_path(self.path)
        ctype = 'text/plain'
        self.send_response(200)
        self.send_header("Content-type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Last-Modified", self.date_time_string(time.time()))
        self.end_headers()
        return data

class OBIHTTPServer(http.HTTPServer,Thread):
    def __init__(self,jobIterator,server_address=('', 0),RequestHandlerClass=OBIServHandler):
        http.HTTPServer.__init__(self,server_address, RequestHandlerClass)
        Thread.__init__(self)
        self.jobIterator = iter(jobIterator)
        self.jobid=0
        self.agent = set()
        self.jobfinished=False
        self.results=deque()
        self.running={}
        self.ip,self.port=self.socket.getsockname()

        
    def __iter__(self):
        self.nextjob=None
        while not self.jobfinished:
            self.handle_request()
            yield self.jobid
            
        while self.agent:
            self.nextjob=None
            self.handle_request()
            
    def run(self):
        print "server is running on port %d" % self.port
        for i in self:
            print "Running jobs %d" %i

class OBIHTTPClient(httplib.HTTPConnection):
    def __init__(self,host, port=8000, strict=False, timeout=10):
        httplib.HTTPConnection.__init__(self, host, port, strict, timeout)
        
def doJobs(host,port=8000,client=OBIHTTPClient):
        ok=True
        while (ok):
            conn=client(host,port)
            Headers = {"OBIAgentID" :"%d" % os.getpid() }
            try:
                conn.request("GET", "/nextjob",None,Headers)
                answer = conn.getresponse()
                if answer.status==601:
                    print "end of jobs"
                    ok=False
                else:
                    data = answer.read()
                    conn.close()
                    print data
                    data=pickle.loads(data)
                    result = JobResult(data)
                    sresult= pickle.dumps(result,0)
                    conn=client(host,port)
                    conn.request("POST", "/result",sresult,Headers)
                    answer = conn.getresponse()
                    if answer.status==602:
                        print "result received"
                        yield result
            except:
                ok=False
            

class TestJob(Jobs):
    def __init__(self,a,b):
        self.a = a
        self.b = b
        
    def __call__(self):
        return self.a + self.b
        
        
def jobiter():
    for i in xrange(10):
        yield TestJob(i,i)
        
def run(server_class=OBIHTTPServer,
        handler_class=OBIServHandler):
    server_address = ('', 0)
    ji=jobiter()
    httpd = server_class(server_address, handler_class,ji)
    print "server is running on port %d" % httpd.port
    for i in httpd:
        print "Running jobs %d" %i
