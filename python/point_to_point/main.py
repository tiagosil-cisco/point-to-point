# -*- mode: python; python-indent: 4 -*-
import ncs
import ipaddress
from ncs.application import Service
# from . import rm_alloc
import resource_manager.ipaddress_allocator as ip_allocator

# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')
        
        pool_name = "P2P_LINKS"
        allocation_name = service.name
        ip_allocator.net_request(service,
                             "/ncs:services/point-to-point:point-to-point[name='%s']" % (service.name),
                             tctx.username,
                             pool_name,
                             allocation_name,
                             30)


        net = ip_allocator.net_read(tctx.username, root,
                                pool_name, allocation_name)

        if not net:
            self.log.info("Alloc not ready")
            return
        
        # ip_prefix = service.ip_prefix
        # subnet = ipaddress.IPv4Network(ip_prefix)
        # ipv4_address_a = subnet.network_address + 1
        # ipv4_address_b = subnet.network_address + 2
        # subnet_mask = subnet.netmask
        
        subnet = ipaddress.IPv4Network(net)
        ipv4_address_a = subnet.network_address + 1
        ipv4_address_b = subnet.network_address + 2
        subnet_mask = subnet.netmask

        vars = ncs.template.Variables()
        vars.add('ipv4_address_a', ipv4_address_a)
        vars.add('ipv4_address_b', ipv4_address_b)
        vars.add('subnet_mask', subnet_mask)
        template = ncs.template.Template(service)
        template.apply('point-to-point-template', vars)

    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_lock_create
    # def cb_pre_lock_create(self, tctx, root, service, proplist):
    #     self.log.info('Service plcreate(service=', service._path, ')')

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service postmod(service=', kp, ')')


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('point-to-point-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
