import logging
import webob
from pyhantom.in_data_types import LaunchConfigurationInput, DeleteLaunchConfigurationInput, DescribeLaunchConfigurationsInput
from pyhantom.out_data_types import LaunchConfigurationType
from pyhantom.util import make_arn, CatchErrorDecorator, log
from pyhantom.wsgiapps import PhantomBaseService


class CreateLaunchConfiguration(PhantomBaseService):
    def __init__(self, name):
        PhantomBaseService.__init__(self, name)

    @webob.dec.wsgify
    @CatchErrorDecorator(appname="CreateLaunchConfiguration")
    def __call__(self, req):
        user_obj = self.get_user_obj(req)

        input = LaunchConfigurationInput()
        input.set_from_dict(req.params)
        lc = LaunchConfigurationType('LaunchConfiguration')
        lc.set_from_intype(input, make_arn(input.LaunchConfigurationName, self.xamznRequestId, 'launchConfigurationName'))

        self._system.create_launch_config(user_obj, lc)

        res = self.get_response()
        doc = self.get_default_response_body_dom()
        res.unicode_body = doc.documentElement.toprettyxml()
        return res


class DeleteLaunchConfiguration(PhantomBaseService):
    def __init__(self, name):
        PhantomBaseService.__init__(self, name)

    @webob.dec.wsgify
    @CatchErrorDecorator(appname="DeleteLaunchConfiguration")
    def __call__(self, req):
        user_obj = self.get_user_obj(req)

        input = DeleteLaunchConfigurationInput()
        input.set_from_dict(req.params)

        self._system.delete_launch_config(user_obj, input.LaunchConfigurationName)
        res = self.get_response()
        doc = self.get_default_response_body_dom()
        res.unicode_body = doc.documentElement.toprettyxml()
        return res


class DescribeLaunchConfigurations(PhantomBaseService):
    def __init__(self, name):
        PhantomBaseService.__init__(self, name)

    @webob.dec.wsgify
    @CatchErrorDecorator(appname="DescribeLaunchConfigurations")
    def __call__(self, req):
        user_obj = self.get_user_obj(req)

        input = DescribeLaunchConfigurationsInput()
        input.set_from_dict(req.params)

        names = None
        if input.LaunchConfigurationNames:
            names = input.LaunchConfigurationNames
        (lc_list, next_token) = self._system.get_launch_configs(user_obj, names=names, max=input.MaxRecords, startToken=input.NextToken)

        res = self.get_response()
        doc = self.get_default_response_body_dom()

        lc_el = doc.createElement('LaunchConfigurations')
        doc.documentElement.appendChild(lc_el)
        if next_token:
            nt_el = doc.createElement('NextToken')
            doc.documentElement.appendChild(nt_el)
            text_element = doc.createTextNode(next_token)
            nt_el.appendChild(text_element)

        lc_list.add_xml(doc, lc_el)
        res.unicode_body = doc.documentElement.toxml()
        log(logging.DEBUG, res.unicode_body)
        return res


