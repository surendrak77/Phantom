import simplejson as json
import sys

fname = sys.argv[1]
f = open(fname, "r")
d  = json.load(f)

user_file = sys.argv[2]
f = open(user_file)
user_list = {}
for l in f:
    l_a = l.split()
    user_list[l_a[0].strip()] = l_a[1].strip()


clouds = {
   'hotel': 'svc.uc.futuregrid.org',
   'sierra': 's83r.idp.sdsc.futuregrid.org',
}

sites = {}
for cloud in clouds:
    name = cloud
    host = clouds[name]

    for user in user_list:
        cloud_site = {}
        cloud_site['driver_class'] = "libcloud.compute.drivers.ec2.NimbusNodeDriver"
        driver_kwargs = {
         'key': user,
         'secret': user_list[user],
         'host': host,
         'port': 8444,
        }
        cloud_site['driver_kwargs'] = driver_kwargs

        site_name = "%s-%s" % (name, user)
        sites[site_name] = cloud_site


d['epuservices']['epu-provisioner-service'][0]['config']['sites'] = sites
out = json.dumps(d, indent='    ')

print out