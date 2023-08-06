from fabric.decorators import task
from fabric.api import env, lcd

@task
def depup(to_tip=False):
    """ Checkout/update external dependencies """
    with lcd(env.local_project_root):
        for vc_dir in env.external_sources:
            vc_dir.checkout_and_update(to_tip)


@task
def depstick():
    """ A handy routing to stick repos with current version """
    with lcd(env.local_project_root):
        for vc_dir in env.external_sources:
            vc_dir.stick_current_version()


@task
def depver():
    """ Show sticky versions, if any """
    with lcd(env.local_project_root):
        for vc_dir in env.external_sources:
            print("{0}: {1}".format(vc_dir.get_sticky_version(),
                                    vc_dir.dest_dir))
