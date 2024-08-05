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
    rm -rf R-${R_VERSION}-1-1.x86_64.rpm &&\
    ln -s /opt/R/${R_VERSION}/bin/R /usr/local/bin/R && \
    ln -s /opt/R/${R_VERSION}/bin/Rscript /usr/local/bin/Rscript && \
    ln -s /opt/R/${R_VERSION}/bin/R /usr/local/bin/R-${R_VERSION}

#Copy Makevars and Renviron
COPY build_files/RFiles/* /opt/R/${R_VERSION}/lib/R/etc/

#Copy script to generate aws credentials
COPY build_files/get-aws-temp-cred-R.py /app/

#configure Java for R and Installing tinytex

RUN  R CMD javareconf \
&& Rscript -e "install.packages('tinytex', repo='https://rspm.pfizer.com/swb_r431/latest')" \
&& Rscript -e "tinytex::install_tinytex(dir='/opt/tinytex/', bundle='TinyTeX', extra_packages='fancybox', add_path=TRUE)" \
&& echo 'Sys.setenv(PATH = paste("/opt/tinytex/bin/x86_64-linux/", Sys.getenv("PATH"),sep=":"))' >> /opt/R/${R_VERSION}/lib/R/etc/Rprofile.site \
&& Rscript -e "tinytex::tlmgr(c('option', 'sys_bin', '/opt/tinytex/bin/x86_64-linux/'))" \
&& chmod -R 777 /opt/tinytex/

ENV PATH=/opt/tinytex/bin/x86_64-linux/:$PATH
ENV DISPLAY=10
ENV NOAWT=1
# setting up the environment variable so that all users can access this makevars file
ENV R_MAKEVARS_SITE=/opt/R/${R_VERSION}/lib/R/etc/Makevars
 
