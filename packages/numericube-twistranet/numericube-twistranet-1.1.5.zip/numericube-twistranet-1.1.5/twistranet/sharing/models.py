"""
Two classes here:
- One to manage the "like" capability (which is basically a UserAccount => Twistable relation)
- One to manage the "share" capability (which is a kind of 'alias').

We just extend the Twistable model with those two methods:
Like() => say you like sth
Share(publisher = None) => Share what you just saw ON YOUR OWN WALL.
    If publisher is set, then you can share what you saw on a specific community or 
    on another user's wall (to give a precise insight)
"""
from django.db import models
from twistranet.twistapp import Twistable

class LikeManager(models.Manager):
    """
    Use this to rapidly and safely retreive likes for a given object.
    Example usage:
        Like.objects.likes(content) => {
            "n_likes":  <integer>,
            "featured": [<authorized_useraccounts>*],
            "i_like":   boolean
        }
    This is used to display "x and x other ppl like this.
    """
    def likes(self, content):
        """
        Return a dict of like info (see class docstring) for the given content.
        """
        from twistranet.twistapp import UserAccount
        
        n_likes = Like.objects.filter(what = content).count()
        if n_likes:
            auth = Twistable.objects._getAuthenticatedAccount()
            featured = UserAccount.objects.filter(_liked__what = content).distinct()
            i_like = Like.objects.filter(what = content, who__id = auth.id).exists()
        else:
            featured = []
            i_like = False
            
        # Return the like structure
        return {
            "n_likes":  n_likes,
            "featured": featured,
            "i_like":   i_like,
        }

class Like(models.Model):
    """
    This is a UserAccount => Twistable relation
    """
    objects = LikeManager()
    
    who = models.ForeignKey("Account", related_name = "_liked", db_index = True, ) 
    what = models.ForeignKey("Twistable", null = False, related_name = "_likes", db_index = True, )
    
    class Meta:
        app_label = 'twistapp'


def like(self):
    """
    Imply you like something
    """
    auth = Twistable.objects._getAuthenticatedAccount()
    
    # We don't allow multiple likes for the same person (of course).
    Like.objects.get_or_create(who = auth, what = self)
    
def likes(self):
    """
    Return likes for current object.
    WARNING: TIME-CONSUMING! WE SHOULD HEAVILY CACHE THIS!
    XXX TODO: HEAVILY CACHE THIS!
    """
    return Like.objects.likes(self)
    
def unlike(self):
    """
    Now you don't like anymore
    """
    auth = Twistable.objects._getAuthenticatedAccount()
    Like.objects.filter(
        who = auth,
        what = self
    ).delete()

def share(self, publisher = None):
    """
    """

# Monkey-patch the Twistable object
Twistable.like = like
Twistable.unlike = unlike
Twistable.likes = likes
Twistable.share = share
