import itertools
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from stdimage import StdImageField
from django_countries.fields import CountryField
from ckeditor.fields import RichTextField
from utils.models import CreationModificationDateMixin
from phonenumber_field.modelfields import PhoneNumberField
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.
from tongoza import settings


class ActiveProfileManager(models.Manager):
    def all(self):
        return super(ActiveProfileManager, self).all().filter(is_active=True)


class ProfileManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class AbstractProfile(CreationModificationDateMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, default='', max_length=255, editable=False)
    aboutMe = models.CharField(max_length=400)
    company = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    education_institution = models.CharField(max_length=200, blank=True, null=True)
    course = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    linkedin = models.CharField(max_length=150, blank=True, null=True)
    facebook = models.CharField(max_length=150, blank=True, null=True)
    twitter = models.CharField(max_length=150, blank=True, null=True)
    telegram_username = models.CharField(max_length=60, blank=True, null=True)
    snapchat_username = models.CharField(max_length=60, blank=True, null=True)
    messenger = models.CharField(max_length=60, blank=True, null=True)
    whatsapp_phone_number = PhoneNumberField(blank=True, null=True)
    country = CountryField(multiple=False, blank=True, null=True)
    city = models.CharField(max_length=60, blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Profile(AbstractProfile):
    government_issued_id = StdImageField(upload_to='tongoza/images/national_identificantions/', blank=True, null=True,
                                         help_text='Required only if you wish to have a dual'
                                                   ' profile for both Tongoza light mode and Tongoza darke mode')

    active = ActiveProfileManager()
    objects = ProfileManager()

    class Meta(AbstractProfile.Meta):
        db_table = 'Light Mode Profile'

    def __str__(self):
        return str(self.user.username)

    def natural_key(self):
        return (self.slug,)

    def get_absolute_url(self):
        return reverse('tongozahome:profile', kwargs={'slug': self.slug})

    def get_image_in_display(self):
        image = self.profileimage_set.filter(in_display=True, dark_mode_pic=False, public=True)
        if image:
            return image[0]

    def get_caption(self):
        image = self.get_image_in_display()
        if image:
            if image.caption:
                return image.caption

    def get_profile_pic(self):
        image = self.profileimage_set.filter(profile_pic=True, dark_mode_pic=False)
        if image:
            return image[0]
        else:
            return self.get_image_in_display()

    def get_dark_profile_pic(self):
        image = self.profileimage_set.filter(profile_pic=True, dark_mode_pic=True)
        if image:
            return image[0]
        else:
            return self.get_image_in_display()

    def get_light_mode_public_images(self):
        images = self.profileimage_set.filter(in_display=False, dark_mode_pic=False, public=True)
        return images

    def get_light_mode_images(self):
        images = self.profileimage_set.filter(in_display=False, dark_mode_pic=False)
        return images

    def _generate_slug(self):
        value = self.user.username
        slug_original = slugify(value, allow_unicode=True)

        slug_candidate = '{}'.format(slug_original)

        return slug_candidate

    def save(self, *args, **kwargs):
        if not self.pk or self.slug != self.user.username:
            print('came to update sluggg')
            self.slug = self._generate_slug()
        if self.get_image_in_display():
            self.is_active = True
        else:
            self.is_active = False

        super().save(*args, **kwargs)


class DisplayImageManager(models.Manager):
    def get_query_set(self):
        return super(DisplayImageManager, self).get_query_set().filter(in_display=True)


class ProfileImage(CreationModificationDateMixin):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    image = StdImageField(upload_to='tongoza/images/profile_images', variations={
        'thumbnail': (250, 250),
        'medium': (420, 236, True),
        'large': (800, 675)
    }, delete_orphans=True)
    caption = models.TextField(blank=True, null=True,
                               help_text="Write something about the moment captured in this image")
    public = models.BooleanField(default=True)
    in_display = models.BooleanField(default=True)
    profile_pic = models.BooleanField(default=True)

    dark_mode_pic = models.BooleanField(default=False)
    displayed = DisplayImageManager()
    objects = models.Manager()

    class Meta:
        ordering = ('-in_display',)

    def __str__(self):
        return str(self.profile)

    def save(self, *args, **kwargs):
        if self.in_display:
            self.profile.active = True
            self.profile.save()

        super().save(*args, **kwargs)


def get_public_posts():
    posts = Post.objects.filter(active=True, public=True)
    return posts


def get_all_posts():
    posts = Post.objects.filter(active=True)
    return posts


class Post(CreationModificationDateMixin):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    # author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField(unique=True,
                            default='',
                            editable=False,
                            max_length=255,
                            )
    title = models.CharField(max_length=100)
    image = StdImageField(upload_to='tongoza/posts/images/products',
                          help_text="upload post cover Image",
                          variations={
                              'thumbnail': (250, 250),
                              'medium': (420, 236, True),
                              'large': (800, 675)
                          }, delete_orphans=True)
    caption = models.TextField(help_text="Inspire your audience with the moment captured in this image")
    public = models.BooleanField(default=True, help_text="Everyone can see this post.")

    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='post_likes')
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.title)

    def get_total_likes(self):
        return self.likes.count()

    def cross_reads(self):
        # orders = Order.objects.filter(items__item=self)
        # order_items = OrderItem.objects.filter(order__in=orders).exclude(item=self)
        posts = Post.objects.all().exclude(slug=self.slug)
        return posts

    def get_absolute_url(self):

        return reverse('tongozahome:postView', kwargs={'slug': self.slug})

    def _generate_slug(self):
        max_length = self._meta.get_field('slug').max_length
        value = self.title
        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Post.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)

        return slug_candidate

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = self._generate_slug()

        super().save(*args, **kwargs)


class Comments(MPTTModel):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments', null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children')
    content = models.TextField()
    publish = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ('publish',)

    def __str__(self):
        return f'Comment by {self.post.author}'
