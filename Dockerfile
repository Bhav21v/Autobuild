FROM redhat/ubi9:latest

ARG R_VERSION=

RUN subscription-manager clean && \
    subscription-manager register --username={{SUBSCRIPTION_USERNAME}} --password={{SUBSCRIPTION_PASSWORD}} && \
    subscription-manager attach --auto && \
    subscription-manager repos --enable codeready-builder-for-rhel-9-x86_64-rpms && \
    dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm && \ 
    dnf clean all 
    
RUN echo "Installing R Base..." && \
    curl -O https://cdn.rstudio.com/r/rhel-9/pkgs/R-${R_VERSION}-1-1.x86_64.rpm && \
    dnf install -y R-${R_VERSION}-1-1.x86_64.rpm && \
    dnf clean all && \
    rm -rf R-${R_VERSION}-1-1.x86_64.rpm 

RUN  R CMD javareconf \
&& Rscript -e "install.packages('abind', repos='https://rspm-dev.pfizer.com:8080/swb_r441/latest', type='source')"
 
