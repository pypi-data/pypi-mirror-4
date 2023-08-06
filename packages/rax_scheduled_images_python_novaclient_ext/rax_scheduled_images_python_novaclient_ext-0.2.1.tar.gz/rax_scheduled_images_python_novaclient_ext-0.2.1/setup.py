#   Copyright 2013 Rackspace
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import setuptools


setuptools.setup(
    name="rax_scheduled_images_python_novaclient_ext",
    version="0.2.1",
    author="Rackspace",
    author_email="eddie.sheffield@rackspace.com",
    url="https://github.com/rackspace-titan/rax_scheduled_images_python_novaclient_ext",
    description='Extends python-novaclient to use RAX-SI, the Rackspace Nova '
                'API Scheduled Images extension',
    license="Apache License, Version 2.0",
    packages=["rax_scheduled_images_python_novaclient_ext"],
    install_requires=["python-novaclient"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ]
)
