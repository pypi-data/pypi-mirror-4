from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
import re
from random import randint


register = template.Library()


SERVICE_NUMBER = getattr(settings, 'AD_SERVICE_NUMBER', '')

AD_SIZES = {
    (728, 90): 'leaderboard-advertisement',
    (300, 250): 'medium-rectangle-advertisement',
    (160, 600): 'wide-skyscraper-advertisement',
    (300, 100): 'three-to-one-rectangle-advertisement',
    (88, 31): 'micro-bar-advertisement',
}


@register.simple_tag
def ad_header():
    ret = """
    <script type="text/javascript">
        var googletag = googletag || {};
        googletag.cmd = googletag.cmd || [];
        (function() {
            var gads = document.createElement("script");
            gads.async = true;
            gads.type = "text/javascript";
            var useSSL = "https:" == document.location.protocol;
            gads.src = (useSSL ? "https:" : "http:") + "//www.googletagservices.com/tag/js/gpt.js";
            var node = document.getElementsByTagName("script")[0];
            node.parentNode.insertBefore(gads, node);
         })();
   </script>"""
    return mark_safe(ret)


@register.simple_tag
def ad_tag(ad_unit):
    matches = re.match(r'^\w+_(?P<width>\d+)x(?P<height>\d+)', ad_unit)
    width = int(matches.group('width'))
    height = int(matches.group('height'))
    class_name = AD_SIZES.get((width, height), '')
    id = "gpt-ad-%d" % randint(1000000000, 9999999999)
    ret = """
    <div id="%(id)s" class="advertisement %(class_name)s" style="height:%(height)dpx; width:%(width)dpx;">
        <script type="text/javascript">
            googletag.cmd.push(function() {
                googletag.pubads().display("/%(service_number)s/%(ad_unit)s", [%(width)d, %(height)d], "%(id)s");
            });
        </script>
    </div>""" % {'id': id,
                 'service_number': SERVICE_NUMBER,
                 'ad_unit': ad_unit,
                 'class_name': class_name,
                 'width': width,
                 'height': height,}
    return mark_safe(ret)
