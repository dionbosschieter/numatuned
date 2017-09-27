from setuptools import setup

setup(name='numatuned',
      version='0.1',
      description='Numad replacement for qemu/libvirtd virtual machines that uses virsh numatune --nodeset to bind a virtual machine to a numa zone',
      url='http://github.com/dionbosschieter/numatuned',
      author='Dion Bosschieter',
      author_email='dbosschieter@transip.nl',
      license='MIT',
      packages=['numatuned', 'numatuned.provisioning', 'numatuned.provisioning.rules'],
      scripts=['bin/numatuned'],
      zip_safe=False)
