## Multi-arch builds

`gtm` has been updated to support building amd64 and arm64 images. 

It currently assumes the local system is amd64 and the remote system is arm64. This
means future work is needed if a developer starts building on arm.


### Remote Build Host
A remote ARM host must be configured with SSH access and Docker for this to work. 

In the specific case of Gigantum developers, a `t4g.xlarge` instance in AWS in the "demos" account
has been configured called `arm-client-builder`. You must connect to this using
the ssh key in 1Password. Further instructions on what IP to use and how to finish
configuring can be found in the notes of the ssh key in 1Password.


### Setup
To perform multi-arch builds there are a few steps to follow.

1. Get a remote host setup
2. Add the ssh key for teh remote build host to your ssh-agent, e.g.:
   
   ```
   ssh-add ~/.ssh/arm-builder.pem
   ```
   
3. Run `gtm dev setup` and provide the IP/hostname for the remote build host (docker must be running as a buildx builder is configured during this step)




### Performing multi-arch builds
Multi-arch builds should be done when preparing for a release and prior to any QA testing.

Make sure the build instance is running and then simply using the `--multi-arch` flag
to enable multi-arch builds.

Remember to shut of the build instance when you are done! This has not yet been
automated, but will in the future.