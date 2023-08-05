import flickrlib
#secret = open('/home/dwight/.flickr_shared_secret')
#apikey = open('/home/dwight/.flickr_api_key')
FLICKR_API_KEY="22e69709a08cca05be7b64ad50eaa2c0"
FLICKR_SECRET="d0cde1bd259c6808"
import flickrengine
username='pigeonflight'
group='ilovefood'
FlickrAgent = flickrengine.FlickrAgent(username)
text=per_page=page=tags=''
if len(group) > 0:
    print FlickrAgent.showphotos(group=group,tags=tags,page=page,per_page=per_page,text=text)

else:
    print FlickrAgent.showphotos(tags=tags,page=page,per_page=per_page,text=text)

"""
agent = flickrlib.FlickrAgent(flickr_api_key,flickr_ssecret)
person = agent.flickr.people.findByUsername(username='pigeonflight')
userid = person[u'id']

count = 1 
photos = agent.flickr.people.getPublicPhotos(user_id=userid, per_page=10, page=count)

pages_count = photos[u'pages']
tagged_photo_list = []
#page = photos[u'page']

while (int(pages_count) >= count):
    page = photos[u'page']
    print "Page %s of %s" % (page, pages_count)
    for photo in photos[u'photo']:
        farm = photo[u'farm']
        server = photo[u'server']
        photo_secret = photo[u'secret']
        photourl = "http://farm%s.static.flickr.com/%s/%s_%s.jpg" % (farm,server,photo[u'id'],photo_secret)
        print photourl
    count = count +1
    photos = agent.flickr.people.getPublicPhotos(user_id=userid, per_page=10, page=count)
"""

photo_tags="birthday"
#photos = agent.flickr.photos.search(user_id=userid, tags=photo_tags)
#print photos

def showphotos( tags="" ):
    result = []
    photos = agent.flickr.photos.search(user_id=userid, tags=tags)
    for photo in photos[u'photo']:
        farm = photo[u'farm']
        server = photo[u'server']
        photo_secret = photo[u'secret']
        photourl = "http://farm%s.static.flickr.com/%s/%s_%s.jpg" % (farm,server,photo[u'id'],photo_secret)
        photourl_medium = "http://farm%s.static.flickr.com/%s/%s_%s_m.jpg" % (farm,server,photo[u'id'],photo_secret)
        photourl_small = "http://farm%s.static.flickr.com/%s/%s_%s_s.jpg" % (farm,server,photo[u'id'],photo_secret)
        list= [photourl,photourl_medium,photourl_small]
        result.append(list)
    return result 


"""
#photos = agent.flickr.people.getPublicPhotos(user_id=userid)
for photo in photos[u'photo']:
    farm = photo[u'farm']
    server = photo[u'server']
    photo_secret = photo[u'secret']
    photourl = "http://farm%s.static.flickr.com/%s/%s_%s.jpg" % (farm,server,photo[u'id'],photo_secret)
    print photourl
    #print photo

pages_count = photos[u'pages']
page = photos[u'page']
print "Page %s of %s" % (pages_count, pages_count)
"""


