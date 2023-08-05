import flickrlib
from Products.flickrgallery.config import FLICKR_API_KEY,FLICKR_SECRET
class FlickrAgent:
    """
    """
    def __init__(self,username=None):
        self.agent = flickrlib.FlickrAgent(FLICKR_API_KEY,FLICKR_SECRET)
        if username: #don't want to hit flickr unnecessarily
            self.person = self.agent.flickr.people.findByUsername(username=username)
            self.userid = self.person[u'id']
             

    def showphotos( self,tags="",page='1',per_page='100',text='',group=''):
        result = []
        if len(group) > 0:
            photos = self.agent.flickr.photos.search(group_id=group,user_id=self.userid, tags=tags,per_page=per_page,page=page,text=text)
        else:
            photos = self.agent.flickr.photos.search(user_id=self.userid, tags=tags,per_page=per_page,page=page,text=text)
        #import pdb; pdb.set_trace()
        try:
            for photo in photos[u'photo']:
                farm = photo[u'farm']
                server = photo[u'server']
                #photo_info = self.getinfo(photo_id=photo[u'id'])
                photo_id = photo[u'id']
                photo_secret = photo[u'secret']
                photo_title = photo[u'title']
                photourl = "http://farm%s.static.flickr.com/%s/%s_%s.jpg" % (farm,server,photo_id,photo_secret)
                photourl_medium = "http://farm%s.static.flickr.com/%s/%s_%s_m.jpg" % (farm,server,photo_id,photo_secret)
                photourl_small = "http://farm%s.static.flickr.com/%s/%s_%s_s.jpg" % (farm,server,photo_id,photo_secret)
                photourl_thumb = "http://farm%s.static.flickr.com/%s/%s_%s_t.jpg" % (farm,server,photo_id,photo_secret)
                photourl_large = "http://farm%s.static.flickr.com/%s/%s_%s_o.jpg" % (farm,server,photo_id,photo_secret)
                #list= [photourl,photourl_medium,photourl_small,photo_id, photo_title]
                imagesize=(photourl_small, photourl_medium, photourl_thumb, photourl_large)
                list= [photourl,imagesize,photo_id, photo_title]
                result.append(list)
            return (result,photos[u'pages'])
        except KeyError:
            return (result,photos[u'pages'])
    
    def getinfo(self, photo_id=""):
        temp = self.agent.flickr.photos.getInfo(photo_id=photo_id)
        title = temp[u'title'][0][u'text']
        desc = temp[u'description'][0][u'text']
        license = temp[u'license']
        lname = self.getlicense_name(license)   
                
        date_taken = temp[u'dates'][0][u'taken']
        info = [title, desc, date_taken , lname]
        return info

    def getlicense_name(self, license=""):
        #import pdb; pdb.set_trace()
        name = ""
        temp_list =  self.agent.flickr.photos.licenses.getInfo()
        license_list = temp_list[u'license']
        for item in license_list:
           if item[u'id'] == license:
              name = item[u'name']
              break

        return name

 
    def getsizes(self, photo_id=""):
        temp = self.agent.flickr.photos.getSizes(photo_id=photo_id)
        temp = temp[u'size'] 
        sizeinfo = [(t[u'label'],t[u'source']) for t in temp]
        return sizeinfo

    def generate_url(self, photo_id="", size="m", download="false"):
        """
        """

        print "from flickr"
        photo = self.agent.flickr.photos.getInfo(photo_id=photo_id)

        farm = photo[u'farm']
        server = photo[u'server']
        photo_secret = photo[u'secret']
        photourl = "http://farm%s.static.flickr.com/%s/%s_%s.jpg" % (farm,server,photo_id,photo_secret)
        i = photourl.rindex('.')
        temp = [photourl[:i],  photourl[i:] ] 

        size_dict = {'sq':'_s', 't':'_t', 's':'_m', 'm':'', 'l':'_o' }
        extension = size_dict[size]
        photourl = temp[0] + size_dict[size] + temp[1]; 

        return photourl
        
