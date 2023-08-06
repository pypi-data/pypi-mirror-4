# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.conf import settings as django_settings
from django.utils.importlib import import_module


COOP_CMS_NAVTREE_CLASS = getattr(django_settings, 'COOP_CMS_NAVTREE_CLASS', 'basic_cms.NavTree')


def get_navigable_content_types():
    ct_choices = []
    try:
        content_apps = django_settings.COOP_CMS_CONTENT_APPS
    except AttributeError:
        content_apps = []
        not_to_be_mapped = ('south', 'django_extensions')
        for m in django_settings.INSTALLED_APPS:
            if(not m.startswith('django.') and m not in not_to_be_mapped):
                content_apps.append(m)
    apps_labels = [app.rsplit('.')[-1] for app in content_apps]
    navigable_content_types = ContentType.objects.filter(app_label__in=apps_labels).order_by('app_label')
    for ct in navigable_content_types:
        is_navnode = ((ct.model == 'navnode') and (ct.app_label == 'coop_cms'))
        if (not is_navnode) and 'get_absolute_url' in dir(ct.model_class()):
            ct_choices.append((ct.id, ct.app_label + u'.' + ct.model))
    return ct_choices


def get_navTree_class():
    if hasattr(get_navTree_class, '_cache_class'):
        return getattr(get_navTree_class, '_cache_class')
    else:
        navTree_class = None
        try:
            full_class_name = getattr(django_settings, 'COOP_CMS_NAVTREE_CLASS')
            module_name, class_name = full_class_name.rsplit('.', 1)
            if not module_name.endswith('models'):
                module_name += '.models'
            module = import_module(module_name)
            navTree_class = getattr(module, class_name)

        except AttributeError:
            if 'coop_cms.apps.basic_cms' in django_settings.INSTALLED_APPS:
                from coop_cms.apps.basic_cms.models import NavTree
                navTree_class = NavTree

        if not navTree_class:
            raise Exception('No NavTree class configured')

        setattr(get_navTree_class, '_cache_class', navTree_class)
        return navTree_class


def get_article_class():
    if hasattr(get_article_class, '_cache_class'):
        return getattr(get_article_class, '_cache_class')
    else:
        article_class = None
        try:
            full_class_name = getattr(django_settings, 'COOP_CMS_ARTICLE_CLASS')
            module_name, class_name = full_class_name.rsplit('.', 1)
            module = import_module(module_name)
            article_class = getattr(module, class_name)

        except AttributeError:
            if 'coop_cms.apps.basic_cms' in django_settings.INSTALLED_APPS:
                from coop_cms.apps.basic_cms.models import Article
                article_class = Article

        if not article_class:
            raise Exception('No article class configured')

        setattr(get_article_class, '_cache_class', article_class)
        return article_class

def get_article_form():
    try:
        full_class_name = getattr(django_settings, 'COOP_CMS_ARTICLE_FORM')
        module_name, class_name = full_class_name.rsplit('.', 1)
        module = import_module(module_name)
        article_form = getattr(module, class_name)

    except AttributeError:
        from coop_cms.forms import ArticleForm
        article_form = ArticleForm

    return article_form





# def get_newsletter_templates(newsletter, user):
#     try:
#         return getattr(django_settings, 'COOP_CMS_NEWSLETTERS_TEMPLATES')
#     except AttributeError:
#         print "# pas de COOP_CMS_NEWSLETTERS_TEMPLATES"
#         return None

# def get_newsletter_form():
#     try:
#         full_class_name = getattr(django_settings, 'COOP_CMS_NEWSLETTER_FORM')
#     except AttributeError:
#         from coop_cms.forms import NewsletterForm
#         newsletter_form = NewsletterForm
#     else:
#         module_name, class_name = full_class_name.rsplit('.', 1)
#         module = import_module(module_name)
#         newsletter_form = getattr(module, class_name)
#     return newsletter_form

def get_article_templates(article, user):
    if hasattr(django_settings, 'COOP_CMS_ARTICLE_TEMPLATES'):
        coop_cms_article_templates = getattr(django_settings, 'COOP_CMS_ARTICLE_TEMPLATES')

        if type(coop_cms_article_templates) in (str, unicode):
            #COOP_CMS_ARTICLE_TEMPLATES is a string :
            # - a function name that will return a tuple
            # - a variable name taht contains a tuple

            #extract module and function/var names
            module_name, object_name = coop_cms_article_templates.rsplit('.', 1)
            module = import_module(module_name) #import module
            article_templates_object = getattr(module, object_name) #get the object
            if callable(article_templates_object):
                #function: call it
                article_templates = article_templates_object(article, user)
            else:
                #var: assign
                article_templates = article_templates_object
        else:
            #COOP_CMS_ARTICLE_TEMPLATES is directly a tuple, assign it
            article_templates = coop_cms_article_templates
    else:
        article_templates = None

    return article_templates

def get_article_logo_size(article):
    try:
        get_size_name = getattr(django_settings, 'COOP_CMS_ARTICLE_LOGO_SIZE')
        try:
            module_name, fct_name = get_size_name.rsplit('.', 1)
            module = import_module(module_name)
            get_size = getattr(module, fct_name)
            if callable(get_size):
                size = get_size(article)
            else:
                size = get_size
        except ValueError:
            size = get_size_name

    except AttributeError:
        size = "48x48"
    return size

# def get_newsletter_item_classes():
#     if hasattr(get_newsletter_item_classes, '_cache_class'):
#         return getattr(get_newsletter_item_classes, '_cache_class')
#     else:
#         item_classes = []
#         try:
#             full_classes_names = getattr(django_settings, 'COOP_CMS_NEWSLETTER_ITEM_CLASSES')
#         except AttributeError:
#             item_classes = (get_article_class(),)
#         else:
#             item_classes = []
#             for full_class_name in full_classes_names:
#                 module_name, class_name = full_class_name.rsplit('.', 1)
#                 module = import_module(module_name)
#                 item_classes.append(getattr(module, class_name))
#             item_classes = tuple(item_classes)

#         if not item_classes:
#             raise Exception('No newsletter item classes configured')

#         setattr(get_newsletter_item_classes, '_cache_class', item_classes)
#         return item_classes
