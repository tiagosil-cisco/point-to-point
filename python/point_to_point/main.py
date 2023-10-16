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
        self.log.debug()
        vars = ncs.template.Variables()
        ipv4_pool_name = "P2P_BB_IPV4"
        ipv6_pool_name = "P2P_BB_IPV6"
        allocation_name = service.name
        ipv4_enabled = service.ipv4_enabled
        ipv6_enabled = service.ipv6_enabled

        if ipv4_enabled:
            ip_allocator.net_request(service,
                                "/ncs:services/point-to-point:point-to-point[name='%s']" % (service.name),
                                tctx.username,
                                ipv4_pool_name,
                                allocation_name,
                                30)


            net = ip_allocator.net_read(tctx.username, root,
                                    ipv4_pool_name, allocation_name)

            if not net:
                self.log.info("Alloc not ready")
                return
            
            
            subnet_v4 = ipaddress.IPv4Network(net)
            ipv4_address_a = subnet_v4.network_address + 1
            ipv4_address_b = subnet_v4.network_address + 2
            mask_v4 = subnet_v4.netmask

            vars.add('ipv4_address_a', ipv4_address_a)
            vars.add('ipv4_address_b', ipv4_address_b)
            vars.add('mask_v4', mask_v4)
        
        else:
            ipv4_address_a = ""
            ipv4_address_b = ""
            mask_v4 = ""

            vars.add('ipv4_address_a', ipv4_address_a)
            vars.add('ipv4_address_b', ipv4_address_b)
            vars.add('mask_v4', mask_v4)

        if ipv6_enabled:
            ip_allocator.net_request(service,
                                "/ncs:services/point-to-point:point-to-point[name='%s']" % (service.name),
                                tctx.username,
                                ipv6_pool_name,
                                allocation_name,
                                64)


            net_v6 = ip_allocator.net_read(tctx.username, root,
                                    ipv6_pool_name, allocation_name)

            if not net_v6:
                self.log.info("Alloc not ready")
                return
            
            
            subnet_v6 = ipaddress.IPv6Network(net_v6)
            ipv6_address_a = subnet_v6.network_address + 1
            ipv6_address_b = subnet_v6.network_address + 2
            mask_v6 = subnet_v6.prefixlen

            vars.add('ipv6_address_a', ipv6_address_a)
            vars.add('ipv6_address_b', ipv6_address_b)
            vars.add('mask_v6', mask_v6)
        
        else:
            ipv6_address_a = ""
            ipv6_address_b = ""
            mask_v6 = ""

            vars.add('ipv6_address_a', ipv6_address_a)
            vars.add('ipv6_address_b', ipv6_address_b)
            vars.add('mask_v6', mask_v6)


        bw = service.bw
        match bw:
            case "1Gbps":
                bw_new = 1000000
            case "10Gbps":
                bw_new = 10000000
            case "40Gbps":
                bw_new = 40000000
            case "100Gbps":
                bw_new = 100000000


        vars.add('bw_new', bw_new)
        vars.add('vrf_a', service.side_a.vrf_a)
        vars.add('vrf_b', service.side_b.vrf_b)
        vars.add('mtu', service.mtu)
        vars.add('device_side_a', "A-NCS5-PE01")
        vars.add('device_side_b', service.side_b.device)
        vars.add('name', service.name)
        
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
