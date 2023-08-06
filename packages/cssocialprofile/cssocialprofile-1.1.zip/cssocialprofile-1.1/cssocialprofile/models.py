from django.db import models
from django.contrib.auth.models import User
from photologue.models import Photo
from cssocialprofile.utils.load_images import loadUrlImage
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

USERTYPE_CHOICES = getattr(settings,'USERTYPE_CHOICES', ((0,'Erabiltzailea'),(1,'Kidea'),(2,'Nor publikoa'),(3,'Kazetaria'),(4,'Administratzailea')))
AUTH_PROFILE_MODULE = getattr(settings,'AUTH_PROFILE_MODULE', 'cssocialprofile.CSSocialProfile')
SOURCE_CHOICES = ((0,'-'),(1,'Register'),(2,'Twitter'),(3,'Facebook'),(4,'OpenId'),)
DEFAULT_PROFILE_PHOTO = getattr(settings,'DEFAULT_PROFILE_PHOTO', 'anonymous-user')


def get_profile_model():
    """ """
    app_label, model_name = AUTH_PROFILE_MODULE.split('.') 
    model = models.get_model(app_label, model_name)
    return model
    
   
class CSAbstractSocialProfile(models.Model):
    user = models.OneToOneField(User,unique=True)
    fullname = models.CharField(_('Full name'), max_length=200, blank=True,null=True)
    bio = models.TextField(_('Biography/description'),null=True,blank=True)
    usertype =  models.PositiveSmallIntegerField(choices = USERTYPE_CHOICES, default = 0)
    
    added_source = models.PositiveSmallIntegerField(choices = SOURCE_CHOICES, default = 0)
    photo = models.ForeignKey(Photo,null=True, blank=True)
    
    twitter_id = models.CharField(max_length=100, blank=True,null=True)
    facebook_id = models.CharField(max_length=100, blank=True,null=True)
    openid_id = models.CharField(max_length=100, blank=True,null=True)
    googleplus_id = models.CharField(max_length=100, blank=True,null=True)


    added = models.DateTimeField(auto_now_add=True,editable=False)
    modified =models.DateTimeField(auto_now=True,editable=False)

    def is_jounalist(self):
        """ """
        return self.usertype==3

    def is_member(self):
        """ """
        return self.usertype==1


    def get_photo(self):
        """ """
        if self.photo:
            return self.photo
        try:
            return Photo.objects.get(title_slug=DEFAULT_PROFILE_PHOTO)
        except:
            return None

    def get_fullname(self):
        """ """
        if self.fullname:
            return self.fullname
        else:
            return u'%s' % (self.user.get_full_name()) or self.user.username            

    def __unicode__(self):
        return u'%s' % (self.user.username)

    class Meta:
        abstract = True
        

class CSSocialProfile(CSAbstractSocialProfile):
    class Meta:
        verbose_name = 'CS Social profile'
        verbose_name_plural = 'CS Social profiles'
        
        
   
def create_profile(sender, instance, created,**kwargs):
    if created:
        model = get_profile_model()
        profile,new = model._default_manager.get_or_create(user=instance) 
from django.db.models.signals import post_save
post_save.connect(create_profile, sender=User)

from social_auth.signals import pre_update
from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend
from social_auth.backends import OpenIDBackend


def get_facebook_photo(response):
    """ """
    import facebook.djangofb as facebook
    
    facebook = facebook.Facebook(settings.FACEBOOK_API_KEY, settings.FACEBOOK_API_SECRET)
    uid = response.get('id')
    user_data = facebook.users.getInfo(uid, ['first_name', 'last_name','pic_big',])[0]
    if user_data:
        img_url = user_data['pic_big']
        img_title = u'Facebook: ' + user_data['first_name'] + u' ' + user_data['last_name']
        return loadUrlImage(img_url,img_title)
    else:
        return None


def get_twitter_photo(response):
    """ """
    img_url = response.get('profile_image_url')
    img_url=img_url.replace('_normal.','.')
    username = response.get('screen_name')
    return loadUrlImage(img_url,u'twitter: ' + username)



def facebook_extra_values(sender, user, response, details, **kwargs):
    """ """
    profile = user.get_profile()
    profile.facebook_id = response.get('id')

    if profile.usertype == 0:
        profile.usertype = 1
    
    if profile.added_source == 0:
        #First time logging in
        profile.added_source = 3
        profile.mota = 1
    if not profile.photo:
        profile.photo = get_facebook_photo(response)
    profile.save()
    #username in facebook users...
    user.username = slugify(user.username)
    user.save()
    
    return True

pre_update.connect(facebook_extra_values, sender=FacebookBackend)


def twitter_extra_values(sender, user, response, details, **kwargs):
    """ """
    model = get_profile_model()
    profile,new = model._default_manager.get_or_create(user=user) 

    if not profile.photo:
        profile.photo = get_twitter_photo(response)
    profile.twitter_id = response.get('screen_name','')

    if profile.usertype == 0:
        profile.usertype = 1
    if profile.added_source == 0:
        profile.added_source = 2

    if not profile.bio:
        profile.bio = response.get('description','')         

    if not profile.fullname:
        profile.fullname = response.get('name','')    

    profile.save()
    return True
pre_update.connect(twitter_extra_values, sender=TwitterBackend)

def openid_extra_values(sender, user, response, details, **kwargs):
    """ """
    profile = user.get_profile()

    if response.status == 'success':
        profile.openid_id = response.getDisplayIdentifier()
        if profile.added_source == 0:
            profile.mota = 1
            profile.added_source = 4
    profile.save()
    return True

pre_update.connect(openid_extra_values, sender=OpenIDBackend)

