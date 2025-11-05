# Build -java subpackage
%if %{defined rhel}
%bcond_with java
%else
%bcond_without java
%endif

# Since version 21.x of the protobuf compiler, the versioning scheme changed.
# For details, see: https://protobuf.dev/support/version-support/

# Language major versions
%global pb_cxx 5
%global pb_java 4

# Base protobuf version
%global pb_release 29.5
#global pb_prerelease rc3
%global so_version %{pb_release}.0
%global pb_version %{pb_release}%{?pb_prerelease:~%{pb_prerelease}}
%global pb_source  %{pb_release}%{?pb_prerelease:-%{pb_prerelease}}

Summary:        Protocol Buffers - Google's data interchange format
Name:           protobuf
# NOTE: perl-Alien-ProtoBuf has an exact-version dependency on the version of
# protobuf with which it was built; it therefore needs to be rebuilt even for
# “patch” updates of protobuf.
Version:        %{pb_version}
Release:        1%{?dist}

# The entire source is BSD-3-Clause, except the following files, which belong
# to the build system; are unpackaged maintainer utility scripts; or are used
# only for building tests that are not packaged—and so they do not affect the
# licenses of the binary RPMs:
#
# Apache-2.0:
#   third_party/googletest/
#     except the following, which are BSD-3-Clause:
#       third_party/googletest/googletest/test/gtest_pred_impl_unittest.cc
#       third_party/googletest/googletest/include/gtest/gtest-param-test.h
#       third_party/googletest/googletest/include/gtest/gtest-param-test.h.pump
#       third_party/googletest/googletest/include/gtest/internal/gtest-param-util-generated.h
#       third_party/googletest/googletest/include/gtest/internal/gtest-param-util-generated.h.pump
#       third_party/googletest/googletest/include/gtest/internal/gtest-type-util.h
#       third_party/googletest/googletest/include/gtest/internal/gtest-type-util.h.pump
License:        BSD-3-Clause
URL:            https://github.com/protocolbuffers/protobuf
Source0:        %{url}/archive/v%{pb_source}/protobuf-%{pb_source}-all.tar.gz

Source1:        ftdetect-proto.vim
Source2:        protobuf-init.el

# Man page hand-written for Fedora in groff_man(7) format based on “protoc
# --help” output.
Source3:        protoc.1

# Restore maven build for java bindings that upstream removed in favour of bazel
# - poms are based on the last release that supported maven build, updated for this release
Patch1:         restore-maven-build.patch
# Disable tests that are failing on 32bit systems
Patch2:         disable-tests-on-32-bit-systems.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=2051202
# java.lang.ClassLoader.defineClass(java.lang.String,byte[],int,int,java.security.ProtectionDomain)
# throws java.lang.ClassFormatError accessible: module java.base does not "opens java.lang" to unnamed module @12d5624a
#	at com.google.protobuf.ServiceTest.testGetPrototype(ServiceTest.java:107)
Patch3:         protobuf-3.19.4-jre17-add-opens.patch
# Fix build with GCC 15 on s390x
# From https://bugzilla.redhat.com/show_bug.cgi?id=2343969#c16
#  and https://github.com/protocolbuffers/protobuf/commit/a2859cc2ce25711613002104022186c0c37d9f1f
Patch6:         protobuf-3.19.6-gcc15.patch
# Backport of patch to use if constexpr
# - https://github.com/protocolbuffers/protobuf/commit/0ea5ccd61c69ff5000631781c6c9a3a50241392c
Patch7:         use-if-constexpr.patch
# Backport of patch to fix LTO-only linker error
# - https://github.com/protocolbuffers/protobuf/commit/3434a21151055b597915f6ff94255a1a195a9ed5
Patch8:         fix-linker-error.patch

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++

BuildRequires:  emacs

BuildRequires:  abseil-cpp-devel
BuildRequires:  gmock-devel
BuildRequires:  gtest-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  zlib-devel

%if %{with java}
%ifnarch %{java_arches}
Obsoletes:      protobuf-java-util < 3.19.4-4
Obsoletes:      protobuf-javadoc < 3.19.4-4
Obsoletes:      protobuf-parent < 3.19.4-4
Obsoletes:      protobuf-bom < 3.19.4-4
Obsoletes:      protobuf-javalite < 3.19.4-4
%endif
%endif

%description
Protocol Buffers are a way of encoding structured data in an efficient
yet extensible format. Google uses Protocol Buffers for almost all of
its internal RPC protocols and file formats.

Protocol buffers are a flexible, efficient, automated mechanism for
serializing structured data – think XML, but smaller, faster, and
simpler. You define how you want your data to be structured once, then
you can use special generated source code to easily write and read
your structured data to and from a variety of data streams and using a
variety of languages. You can even update your data structure without
breaking deployed programs that are compiled against the "old" format.

%package compiler
Summary:        Protocol Buffers compiler

%description compiler
This package contains Protocol Buffers compiler for all programming
languages

%package devel
Summary:        Protocol Buffers C++ headers and libraries
Requires:       jsoncpp-devel
Requires:       zlib-devel
Obsoletes:      protobuf-static < 3.19.6-4

%description devel
Protocol Buffers are a way of encoding structured data in an efficient
yet extensible format. Google uses Protocol Buffers for almost all of
its internal RPC protocols and file formats.

This package installs development headers and libraries for C++.

%package lite
Summary:        Protocol Buffers LITE_RUNTIME libraries

%description lite
Protocol Buffers built with optimize_for = LITE_RUNTIME.

The "optimize_for = LITE_RUNTIME" option causes the compiler to generate code
which only depends libprotobuf-lite, which is much smaller than libprotobuf but
lacks descriptors, reflection, and some other features.

%package lite-devel
Summary:        Protocol Buffers LITE_RUNTIME development libraries
Requires:       protobuf-devel = %{version}-%{release}
Obsoletes:      protobuf-lite-static < 3.19.6-4

%description lite-devel
Protocol Buffers built with optimize_for = LITE_RUNTIME.

The "optimize_for = LITE_RUNTIME" option causes the compiler to generate code
which only depends libprotobuf-lite, which is much smaller than libprotobuf but
lacks descriptors, reflection, and some other features.

This package installs development headers and libraries for C++.

%package vim
Summary:        Vim syntax highlighting for Google Protocol Buffers descriptions
BuildArch:      noarch
# We don’t really need vim or vim-enhanced to be already installed in order to
# install a plugin for it. We do need to depend on vim-filesystem, which
# provides the necessary directory structure.
Requires:       vim-filesystem

%description vim
This package contains syntax highlighting for Google Protocol Buffers
descriptions in Vim editor


%if %{with java}
%ifarch %{java_arches}

%package java
Summary:        Java Protocol Buffers runtime library
Version:        %{pb_java}.%{pb_version}
BuildArch:      noarch
BuildRequires:  maven-local-openjdk25
BuildRequires:  mvn(com.google.code.findbugs:jsr305)
BuildRequires:  mvn(com.google.code.gson:gson)
BuildRequires:  mvn(com.google.guava:guava)
BuildRequires:  mvn(com.google.guava:guava-testlib)
BuildRequires:  mvn(junit:junit)
BuildRequires:  mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-antrun-plugin)
BuildRequires:  mvn(org.codehaus.mojo:build-helper-maven-plugin)
BuildRequires:  mvn(org.mockito:mockito-core)
# To be used only with the protobuf compiler of the same version
Conflicts:      protobuf-compiler > %{pb_version}
Conflicts:      protobuf-compiler < %{pb_version}

%description java
This package contains Java Protocol Buffers runtime library.

%package javalite
Summary:        Java Protocol Buffers lite runtime library
Version:        %{pb_java}.%{pb_version}
BuildArch:      noarch

%description javalite
This package contains Java Protocol Buffers lite runtime library.

%package java-util
Summary:        Utilities for Protocol Buffers
Version:        %{pb_java}.%{pb_version}
BuildArch:      noarch

%description java-util
Utilities to work with protos. It contains JSON support
as well as utilities to work with proto3 well-known types.

%package javadoc
Summary:        Javadoc for protobuf-java
Version:        %{pb_java}.%{pb_version}
BuildArch:      noarch

%description javadoc
This package contains the API documentation for protobuf-java.

%package parent
Summary:        Protocol Buffer Parent POM
Version:        %{pb_java}.%{pb_version}
BuildArch:      noarch

%description parent
Protocol Buffer Parent POM.

%package bom
Summary:        Protocol Buffer BOM POM
Version:        %{pb_java}.%{pb_version}
BuildArch:      noarch

%description bom
Protocol Buffer BOM POM.

%endif
%endif

%package emacs
Summary:        Emacs mode for Google Protocol Buffers descriptions
BuildArch:      noarch
Requires:       emacs-filesystem >= %{_emacs_version}

%description emacs
This package contains syntax highlighting for Google Protocol Buffers
descriptions in the Emacs editor.

%prep
%setup -q -n protobuf-%{pb_source}
%patch 1 -p1 -b .maven
%ifarch %{ix86}
# Need to disable more tests that fail on 32bit arches only
%patch 2 -p0
%endif
%patch 3 -p1 -b .jre17
%patch 6 -p1 -b .gcc15
%patch 7 -p1 -b .if-constexpr
%patch 8 -p1 -b .link-error

# Remove a test that fails
sed -i -e '/command_line_interface_unittest/d' src/file_lists.cmake

find -name \*.cc -o -name \*.h | xargs chmod -x
find examples -type f | xargs chmod 0644

%if %{with java}
%ifarch %{java_arches}
pushd java
%pom_remove_dep com.google.errorprone:error_prone_annotations util
%pom_remove_dep com.google.j2objc:j2objc-annotations util
%pom_remove_dep com.google.truth:truth . core lite util
%pom_remove_plugin :animal-sniffer-maven-plugin . util
popd

# Remove annotation libraries we don't have
annotations=$(
    find -name '*.java' |
      xargs grep -h -e '^import com\.google\.errorprone\.annotation' \
                    -e '^import com\.google\.j2objc\.annotations' |
      sort -u | sed 's/.*\.\([^.]*\);/\1/' | paste -sd\|
)
find -name '*.java' | xargs sed -ri \
    "s/^import .*\.($annotations);//;s/@($annotations)"'\>\s*(\((("[^"]*")|([^)]*))\))?//g'

# Backward compatibility symlink
%mvn_file :protobuf-java:jar: protobuf/protobuf-java protobuf
%endif
%endif

rm -f src/solaris/libstdc++.la


%build
iconv -f iso8859-1 -t utf-8 CONTRIBUTORS.txt > CONTRIBUTORS.txt.utf8
mv CONTRIBUTORS.txt.utf8 CONTRIBUTORS.txt

%cmake . -G Ninja \
  -Dprotobuf_BUILD_TESTS:BOOL=ON \
  -Dprotobuf_BUILD_CONFORMANCE:BOOL=ON \
  -Dprotobuf_BUILD_LIBPROTOC:BOOL=ON \
  -Dprotobuf_BUILD_LIBUPB:BOOL=OFF \
  -Dprotobuf_ABSL_PROVIDER:STRING="package" \
  -Dprotobuf_JSONCPP_PROVIDER:STRING="package" \
  -Dprotobuf_USE_EXTERNAL_GTEST:BOOL=ON
%cmake_build

%if %{with java}
%ifarch %{java_arches}
%ifarch %{ix86} s390x
export MAVEN_OPTS=-Xmx1024m
%endif
export PROTOC=$(pwd)/%_vpath_builddir/protoc
# Skip tests due to missing BR on com.google.truth:truth
%mvn_build -s -- -f java/pom.xml -Dprotoc=$PROTOC -Dmaven.test.skip=true
%endif
%endif

%{_emacs_bytecompile} editors/protobuf-mode.el


%check
%ctest


%install
%cmake_install
find %{buildroot} -type f -name "*.la" -exec rm -f {} +
find %{buildroot} -type f -name "*.o" -exec rm -f {} +
find %{buildroot} -type f -name "*.a" -exec rm -f {} +

# protoc.1 man page
install -p -m 0644 -D -t '%{buildroot}%{_mandir}/man1' '%{SOURCE3}'

install -p -m 644 -D %{SOURCE1} %{buildroot}%{_datadir}/vim/vimfiles/ftdetect/proto.vim
install -p -m 644 -D editors/proto.vim %{buildroot}%{_datadir}/vim/vimfiles/syntax/proto.vim

%if %{with java}
%ifarch %{java_arches}
%mvn_install
%endif
%endif

mkdir -p %{buildroot}%{_emacs_sitelispdir}/protobuf
install -p -m 0644 editors/protobuf-mode.el %{buildroot}%{_emacs_sitelispdir}/protobuf
install -p -m 0644 editors/protobuf-mode.elc %{buildroot}%{_emacs_sitelispdir}/protobuf
mkdir -p %{buildroot}%{_emacs_sitestartdir}
install -p -m 0644 %{SOURCE2} %{buildroot}%{_emacs_sitestartdir}


%files
%doc CONTRIBUTORS.txt README.md SECURITY.md
%license LICENSE
%{_libdir}/libprotobuf.so.%{so_version}
%{_libdir}/libutf8_range.so
%{_libdir}/libutf8_validity.so

%files compiler
%doc README.md
%license LICENSE
%dir %{_includedir}/google
%dir %{_includedir}/google/protobuf
%{_includedir}/google/protobuf/*.proto
%dir %{_includedir}/google/protobuf/compiler
%{_includedir}/google/protobuf/compiler/*.proto
%{_bindir}/protoc
%{_bindir}/protoc-%{so_version}
%{_mandir}/man1/protoc.1*
%{_libdir}/libprotoc.so.%{so_version}

%files devel
%dir %{_includedir}/google
%{_includedir}/google/protobuf/
%exclude %{_includedir}/google/protobuf/*.proto
%exclude %{_includedir}/google/protobuf/compiler/*.proto
%{_includedir}/upb/
%{_includedir}/upb_generator/
%{_includedir}/utf8_range.h
%{_includedir}/utf8_validity.h
%{_libdir}/libprotobuf.so
%{_libdir}/libprotoc.so
%{_libdir}/cmake/protobuf
%{_libdir}/cmake/utf8_range
%{_libdir}/pkgconfig/protobuf.pc
%{_libdir}/pkgconfig/utf8_range.pc
%doc examples/add_person.cc examples/addressbook.proto examples/list_people.cc examples/Makefile examples/README.md

%files emacs
%license LICENSE
%{_emacs_sitelispdir}/protobuf/
%{_emacs_sitestartdir}/protobuf-init.el

%files lite
%license LICENSE
%{_libdir}/libprotobuf-lite.so.%{so_version}

%files lite-devel
%{_libdir}/libprotobuf-lite.so
%{_libdir}/pkgconfig/protobuf-lite.pc

%files vim
%license LICENSE
%{_datadir}/vim/vimfiles/ftdetect/proto.vim
%{_datadir}/vim/vimfiles/syntax/proto.vim

%if %{with java}
%ifarch %{java_arches}

%files java -f .mfiles-protobuf-java
%doc examples/AddPerson.java examples/ListPeople.java
%doc java/README.md
%license LICENSE

%files java-util -f .mfiles-protobuf-java-util
%license LICENSE

%files javadoc -f .mfiles-javadoc
%license LICENSE

%files parent -f .mfiles-protobuf-parent
%license LICENSE

%files bom -f .mfiles-protobuf-bom
%license LICENSE

%files javalite -f .mfiles-protobuf-javalite
%license LICENSE

%endif
%endif


%changelog
* Tue Nov 04 2025 Mat Booth <mat.booth@gmail.com> - 29.5-1
- Update protobuf to 29.5
- Drop upstreamed patches
- Upstream build moved to cmake
- Remove python machinery, python binaries now shipped in separate
  python-protobuf package
- Install *.proto headers with compiler, which should be usable
  without the C++ devel package installed
- Drop some ancient obsoletes and unnecessary requires
- Restore maven build of java bindings

* Sun Sep 28 2025 Yaakov Selkowitz <yselkowi@redhat.com> - 3.19.6-19
- Rebuilt for java-25-openjdk as system jdk

* Fri Sep 19 2025 Python Maint <python-maint@redhat.com> - 3.19.6-18
- Rebuilt for Python 3.14.0rc3 bytecode

* Fri Aug 15 2025 Python Maint <python-maint@redhat.com> - 3.19.6-17
- Rebuilt for Python 3.14.0rc2 bytecode

* Tue Jul 29 2025 Yaakov Selkowitz <yselkowi@redhat.com> - 3.19.6-16
- Convert to pyproject macros

* Fri Jul 25 2025 Fedora Release Engineering <releng@fedoraproject.org> - 3.19.6-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_43_Mass_Rebuild

* Tue Jun 17 2025 Miro Hrončok <mhroncok@redhat.com> - 3.19.6-14
- Build with recent GCC

* Tue Jun 17 2025 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.19.6-13
- Temporarily use GCC 14 to workaround FTBFS on i686 and s390x
- Don’t build Python extension with C++ on Python 3.14+

* Mon Jun 02 2025 Python Maint <python-maint@redhat.com> - 3.19.6-12
- Rebuilt for Python 3.14

* Sat Jan 18 2025 Fedora Release Engineering <releng@fedoraproject.org> - 3.19.6-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Fri Jul 19 2024 Fedora Release Engineering <releng@fedoraproject.org> - 3.19.6-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Fri Jun 07 2024 Python Maint <python-maint@redhat.com> - 3.19.6-9
- Rebuilt for Python 3.13

* Fri Jan 26 2024 Fedora Release Engineering <releng@fedoraproject.org> - 3.19.6-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Sun Jan 21 2024 Fedora Release Engineering <releng@fedoraproject.org> - 3.19.6-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Fri Jul 21 2023 Fedora Release Engineering <releng@fedoraproject.org> - 3.19.6-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Tue Jun 13 2023 Python Maint <python-maint@redhat.com> - 3.19.6-5
- Rebuilt for Python 3.12

* Wed Apr 26 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 3.19.6-4
- Stop packaging static libraries
- Stop using deprecated %%patchN syntax

* Tue Apr 25 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 3.19.6-3
- Remove unnecessary explicit pkgconfig dependencies
- Remove an obsolete workaround for failing Java tests
- Remove conditionals for retired 32-bit ARM architecture
- Remove a slow-test workaround on s390x
- Reduce macro indirection in the spec file

* Fri Jan 20 2023 Fedora Release Engineering <releng@fedoraproject.org> - 3.19.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Wed Dec 07 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 3.19.6-1
- Update to 3.19.6; fix CVE-2022-3171

* Wed Dec 07 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 3.19.5-1
- Update to 3.19.5; fix CVE-2022-1941

* Sun Dec 04 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 3.19.4-7
- Update License to SPDX
- Improved handling of gtest sources
- Update/correct gtest commit hash to match upstream
- Simplify the Source0 URL with a macro
- Drop manual dependency on python3-six, no longer needed
- Drop obsolete python_provide macro
- Drop python3_pkgversion macro
- Update summary and description to refer to “Python” instead of “Python 3”
- Re-enable compiled Python extension on Python 3.11
- Ensure all subpackages always have LICENSE, or depend on something that does
- Remove obsolete ldconfig_scriptlets macros
- The -vim subpackage now depends on vim-filesystem, no longer on vim-enhanced
- Add a man page for protoc
- Use a macro to avoid repeating the .so version, and improve .so globs

* Sun Aug 14 2022 Orion Poplawski <orion@nwra.com> - 3.19.4-6
- Build python support with C++ (bz#2107921)

* Fri Jul 22 2022 Fedora Release Engineering <releng@fedoraproject.org> - 3.19.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Wed Jul 06 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 3.19.4-4
- Exclude java subpackages on non-java arches (fix RHBZ#2104092)
- Obsolete java subpackages on non-java arches

* Mon Jun 13 2022 Python Maint <python-maint@redhat.com> - 3.19.4-3
- Rebuilt for Python 3.11

* Sun Feb 13 2022 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.19.4-2
- Add some --add-opens option for java17
- Restrict heap usage for mvn also on %%ix86

* Mon Feb 07 2022 Orion Poplawski <orion@nwra.com> - 3.19.4-1
- Update to 3.19.4

* Sat Feb 05 2022 Jiri Vanek <jvanek@redhat.com> - 3.19.0-4
- Rebuilt for java-17-openjdk as system jdk

* Fri Jan 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 3.19.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Wed Nov 10 2021 Orion Poplawski <orion@nwra.com> - 3.19.0-2
- Re-enable java

* Wed Oct 27 2021 Major Hayden <major@mhtx.net> - 3.19.0-1
- Update to 3.19.1

* Fri Oct 22 2021 Adrian Reber <adrian@lisas.de> - 3.18.1-2
- Disable tests that fail on 32bit arches

* Thu Oct 14 2021 Orion Poplawski <orion@nwra.com> - 3.18.1-1
- Update to 3.18.1

* Fri Jul 23 2021 Fedora Release Engineering <releng@fedoraproject.org> - 3.14.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Fri Jun 04 2021 Python Maint <python-maint@redhat.com> - 3.14.0-5
- Rebuilt for Python 3.10

* Thu May 06 2021 Adrian Reber <adrian@lisas.de> - 3.14.0-4
- Reintroduce the emacs subpackage to avoid file conflicts between
  protobuf-compiler.x86_64 and protobuf-compiler.i686

* Tue Mar 30 2021 Jonathan Wakely <jwakely@redhat.com> - 3.14.0-3
- Rebuilt for removed libstdc++ symbol (#1937698)

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 3.14.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Jan 04 2021 Adrian Reber <adrian@lisas.de> - 3.14.0-1
- Update to 3.14.0

* Wed Aug 26 2020 Charalampos Stratakis <cstratak@redhat.com> - 3.13.0-1
- Update to 3.13.0

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.12.3-4
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.12.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sat Jul 11 2020 Jiri Vanek <jvanek@redhat.com> - 3.12.3-2
- Rebuilt for JDK-11, see https://fedoraproject.org/wiki/Changes/Java11

* Fri Jun 19 2020 Adrian Reber <adrian@lisas.de> - 3.12.3-2
- Update to 3.12.3

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 3.11.4-2
- Rebuilt for Python 3.9

* Tue Mar 31 2020 Adrian Reber <adrian@lisas.de> - 3.11.4-1
- Update to 3.11.4

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.11.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Dec 18 2019 Adrian Reber <adrian@lisas.de> - 3.11.2-1
- Update to 3.11.2

* Tue Nov 19 2019 Miro Hrončok <mhroncok@redhat.com> - 3.6.1-9
- Drop python2-protobuf (#1765879)

* Sat Oct 26 2019 Orion Poplawski <orion@nwra.com> - 3.6.1-8
- Drop obsolete BR on python-google-apputils

* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 3.6.1-7
- Rebuilt for Python 3.8.0rc1 (#1748018)

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 3.6.1-6
- Rebuilt for Python 3.8

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3.6.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed May 8 2019 Orion Poplawski <orion@nwra.com> - 3.6.1-4
- Update emacs packaging to comply with guidelines

* Wed Feb 27 2019 Orion Poplawski <orion@nwra.com> - 3.6.1-3
- Update googletest to 1.8.1 to re-enable tests

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3.6.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Oct 23 2018 Felix Kaechele <heffer@fedoraproject.org> - 3.6.1-1
- update to 3.6.1
- obsolete javanano subpackage; discontinued upstream

* Fri Jul 27 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 3.5.0-8
- Rebuild for new binutils

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.5.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 3.5.0-6
- Rebuilt for Python 3.7

* Wed Feb 21 2018 Iryna Shcherbina <ishcherb@redhat.com> - 3.5.0-5
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 3.5.0-4
- Escape macros in %%changelog

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.5.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Feb 02 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 3.5.0-2
- Switch to %%ldconfig_scriptlets

* Thu Nov 23 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 3.5.0-1
- Update to 3.5.0

* Mon Nov 13 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 3.4.1-1
- Update to 3.4.1

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jun 27 2017 Mat Booth <mat.booth@redhat.com> - 3.3.1-2
- Make OSGi dependency on sun.misc package optional. This package is not
  available in all execution environments and will not be available in Java 9.

* Mon Jun 12 2017 Orion Poplawski <orion@cora.nwra.com> - 3.3.1-1
- Update to 3.3.1

* Mon May 15 2017 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Jan 27 2017 Orion Poplawski <orion@cora.nwra.com> - 3.2.0-1
- Update to 3.2.0 final

* Mon Jan 23 2017 Orion Poplawski <orion@cora.nwra.com> - 3.2.0-0.1.rc2
- Update to 3.2.0rc2

* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 3.1.0-6
- Rebuild for Python 3.6

* Sat Nov 19 2016 Orion Poplawski <orion@cora.nwra.com> - 3.1.0-5
- Disable slow test on arm

* Fri Nov 18 2016 Orion Poplawski <orion@cora.nwra.com> - 3.1.0-4
- Ship python 3 module

* Fri Nov 18 2016 Orion Poplawski <orion@cora.nwra.com> - 3.1.0-3
- Fix jar file compat symlink

* Fri Nov 18 2016 Orion Poplawski <orion@cora.nwra.com> - 3.1.0-2
- Add needed python requirement

* Fri Nov 04 2016 Orion Poplawski <orion@cora.nwra.com> - 3.1.0-2
- Make various sub-packages noarch

* Fri Nov 04 2016 gil cattaneo <puntogil@libero.it> 3.1.0-2
- enable javanano
- minor changes to adapt to current guidelines

* Fri Nov 04 2016 Orion Poplawski <orion@cora.nwra.com> - 3.1.0-1
- Update to 3.1.0

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.1-5
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 20 2016 Orion Poplawski <orion@cora.nwra.com> - 2.6.1-3
- Tests no longer segfaulting on arm

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Apr 6 2015 Orion Poplawski <orion@cora.nwra.com> - 2.6.1-1
- Update to 2.6.1
- New URL
- Cleanup spec
- Add patch to fix emacs compilation with emacs 24.4
- Drop java-fixes patch, use pom macros instead
- Add BR on python-google-apputils and mvn(org.easymock:easymock)
- Run make check
- Make -static require -devel (bug #1067475)

* Thu Mar 26 2015 Kalev Lember <kalevlember@gmail.com> - 2.6.0-4
- Rebuilt for GCC 5 ABI change

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 2.6.0-3
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Wed Dec 17 2014 Peter Lemenkov <lemenkov@gmail.com> - 2.6.0-2
- Added missing Requires zlib-devel to protobuf-devel (see rhbz #1173343). See
  also rhbz #732087.

* Sun Oct 19 2014 Conrad Meyer <cemeyer@uw.edu> - 2.6.0-1
- Bump to upstream release 2.6.0 (rh# 1154474).
- Rebase 'java fixes' patch on 2.6.0 pom.xml.
- Drop patch #3 (fall back to generic GCC atomics if no specialized atomics
  exist, e.g. AArch64 GCC); this has been upstreamed.

* Sun Oct 19 2014 Conrad Meyer <cemeyer@uw.edu> - 2.5.0-11
- protobuf-emacs requires emacs(bin), not emacs (rh# 1154456)

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Jun 16 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.5.0-9
- Update to current Java packaging guidelines

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Mar 04 2014 Stanislav Ochotnicky <sochotnicky@redhat.com> - 2.5.0-7
- Use Requires: java-headless rebuild (#1067528)

* Thu Dec 12 2013 Conrad Meyer <cemeyer@uw.edu> - 2.5.0-6
- BR python-setuptools-devel -> python-setuptools

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu May 16 2013 Dan Horák <dan[at]danny.cz> - 2.5.0-4
- export the new generic atomics header (rh #926374)

* Mon May 6 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 2.5.0-3
- Add support for generic gcc atomic operations (rh #926374)

* Sat Apr 27 2013 Conrad Meyer <cemeyer@uw.edu> - 2.5.0-2
- Remove changelog history from before 2010
- This spec already runs autoreconf -fi during %%build, but bump build for
  rhbz #926374

* Sat Mar 9 2013 Conrad Meyer <cemeyer@uw.edu> - 2.5.0-1
- Bump to latest upstream (#883822)
- Rebase gtest, maven patches on 2.5.0

* Tue Feb 26 2013 Conrad Meyer <cemeyer@uw.edu> - 2.4.1-12
- Nuke BR on maven-doxia, maven-doxia-sitetools (#915620)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.1-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 2.4.1-10
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Sun Jan 20 2013 Conrad Meyer <konrad@tylerc.org> - 2.4.1-9
- Fix packaging bug, -emacs-el subpackage should depend on -emacs subpackage of
  the same version (%%version), not the emacs version number...

* Thu Jan 17 2013 Tim Niemueller <tim@niemueller.de> - 2.4.1-8
- Added sub-package for Emacs editing mode

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Mar 19 2012 Dan Horák <dan[at]danny.cz> - 2.4.1-6
- disable test-suite until g++ 4.7 issues are resolved

* Mon Mar 19 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 2.4.1-5
- Update to latest java packaging guidelines

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.1-4
- Rebuilt for c++ ABI breakage

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Sep 27 2011 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.4.1-2
- Adding zlib-devel as BR (rhbz: #732087)

* Thu Jun 09 2011 BJ Dierkes <wdierkes@rackspace.com> - 2.4.1-1
- Latest sources from upstream.
- Rewrote Patch2 as protobuf-2.4.1-java-fixes.patch

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Jan 13 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 2.3.0-6
- Fix java subpackage bugs #669345 and #669346
- Use new maven plugin names
- Use mavenpomdir macro for pom installation

* Mon Jul 26 2010 David Malcolm <dmalcolm@redhat.com> - 2.3.0-5
- generalize hardcoded reference to 2.6 in python subpackage %%files manifest

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 2.3.0-4
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Thu Jul 15 2010 James Laska <jlaska@redhat.com> - 2.3.0-3
- Correct use of %%bcond macros

* Wed Jul 14 2010 James Laska <jlaska@redhat.com> - 2.3.0-2
- Enable python and java sub-packages

* Tue May 4 2010 Conrad Meyer <konrad@tylerc.org> - 2.3.0-1
- bump to 2.3.0
