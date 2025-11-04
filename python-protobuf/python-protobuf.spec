%global pypi_name protobuf

# Since version 21.x of the protobuf compiler, the versioning scheme changed.
# For details, see: https://protobuf.dev/support/version-support/
%global pb_version 29.5

Name:           python-%{pypi_name}
Version:        5.%{pb_version}
Release:        1%{?dist}
Summary:        Protocol Buffers are an extensible mechanism for serializing structured data

License:        BSD-3-Clause
URL:            https://github.com/protocolbuffers/protobuf
Source:         %{pypi_source %{pypi_name}}

BuildRequires:  gcc
BuildRequires:  python3-devel

%description
Protocol Buffers (a.k.a., protobuf) are Google's language-neutral,
platform-neutral, extensible mechanism for serializing structured data.

%package -n     python3-%{pypi_name}
Summary:        %{summary}
Provides:       protobuf-python3 = %{version}-%{release}
# To be used only with the protobuf compiler of the same version
Conflicts:      protobuf-compiler > %{pb_version}
Conflicts:      protobuf-compiler < %{pb_version}

%description -n python3-%{pypi_name}
Protocol Buffers (a.k.a., protobuf) are Google's language-neutral,
platform-neutral, extensible mechanism for serializing structured data.

%prep
%autosetup -p1 -n %{pypi_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files google

%files -n python3-%{pypi_name} -f %{pyproject_files}
%{python3_sitearch}/protobuf-%{version}-*-nspkg.pth
%license LICENSE
%doc README.md

%changelog
* Tue Nov 04 2025 Mat Booth <mat.booth@gmail.com> - 5.29.5-1
- Initial package
