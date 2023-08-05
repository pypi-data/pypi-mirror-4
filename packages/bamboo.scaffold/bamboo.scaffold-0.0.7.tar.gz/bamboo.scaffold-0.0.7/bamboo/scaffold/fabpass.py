
import fabric

def setpass(confd):
    #absolutely and utterly needs replacing with ssh keys...RealSoonNow
    try:
        fabric.state.env['user']= confd['bamboo_deployagent'] #'deployagent'
        fabric.state.env['key_filename'] = confd['bamboo_deployagent_keypath'] #/home/deployagent/.ssh/deployagent'
    except Exception, e:
        print 'Avoiding raising this: %s' % e

    
