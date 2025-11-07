Name:           mysql-connector-java
Epoch:          1
Version:        9.3.0
Release:        %autorelease
Summary:        Official JDBC driver for MySQL
License:        GPL-2.0-only
URL:            https://dev.mysql.com/downloads/connector/j/
BuildArch:      noarch
ExclusiveArch:  %{java_arches} noarch

# Generated with generate-tarball.sh
Source0:        %{name}-%{version}-nojars.tar.xz
Source1:        generate-tarball.sh

Patch:          0001-remove-AuthenticationOciClient-plugin.patch
Patch:          0002-Remove-StatementsTest.patch
Patch:          0003-Port-to-Java-21.patch
Patch:          0004-Remove-OpenTelemetry-support.patch
Patch:          0005-Fix-javadoc-generation.patch

# The new name for mysql-connector-java
Provides:       mysql-connector-j = %{epoch}:%{version}-%{release}

# Version 4 of the Java language bindings for protobuf are required
Requires:       mvn(com.google.protobuf:protobuf-java) >= 4.29.0

BuildRequires:  javapackages-local-openjdk25
BuildRequires:  ant-junit
BuildRequires:  ant-junit5
BuildRequires:  apiguardian
BuildRequires:  javassist
BuildRequires:  protobuf-java
BuildRequires:  slf4j

%description
MySQL Connector/J is a native Java driver that converts JDBC (Java Database
Connectivity) calls into the network protocol used by the MySQL database.
It lets developers working with the Java programming language easily build
programs and applets that interact with MySQL and connect all corporate
data, even in a heterogeneous environment. MySQL Connector/J is a Type
IV JDBC driver and has a complete JDBC feature set that supports the
capabilities of MySQL.

%prep
%autosetup -p1 -C

# Remove pom dependency on Oracle OCI that we patched out
%pom_remove_dep :oci-java-sdk-common src/build/misc/pom.xml

# This library is now known as "mysql-connector-j" so install aliases and symlinks
# for the legacy name of "mysql-connector-java"
%mvn_file com.mysql:mysql-connector-j mysql-connector-j mysql-connector-java
%mvn_alias com.mysql:mysql-connector-j mysql:mysql-connector-java

# Many test fail with "CommunicationsException: Communications link failure. The
# last packet sent successfully to the server was 0 milliseconds ago. The driver
# has not received any packets from the server."
rm src/test/java/com/mysql/cj/util/{StringUtilsTest,StringInspectorTest}.java
rm src/test/java/testsuite/regression/*
rm src/test/java/testsuite/simple/*

%build
ant -Dcom.mysql.cj.build.jdk=%{java_home} \
    -Dcom.mysql.cj.extra.libs=%{_javadir} \
    -Dcom.mysql.cj.build.driver.version.snapshot="" \
    -Dcom.mysql.cj.build.git.branch="release/%{version}" \
    test package

%install
%mvn_artifact dist/workspace/*_maven/mysql-connector-j-%{version}.pom \
              dist/workspace/*_maven/mysql-connector-j-%{version}.jar
%mvn_install

%files -f .mfiles
%doc CHANGES README README.md SECURITY.md
%license LICENSE

%changelog
%autochangelog
