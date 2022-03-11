%bcond_without check

# https://github.com/jingweno/ccat
%global goipath         github.com/jingweno/ccat
Version:                1.1.0

%gometa

%global golicenses      LICENSE
%global godocs          README.md

Name:           ccat
Release:        1%{dist}
Summary:        Colorizing `cat`

License:        MIT
URL:            %{gourl}
Source0:        %{gosource}

BuildRequires:  golang(github.com/mattn/go-colorable)
BuildRequires:  golang(github.com/mattn/go-isatty)
BuildRequires:  golang(github.com/sourcegraph/syntaxhighlight)
BuildRequires:  golang(github.com/spf13/cobra)

%description
Colorizing `cat`

%gopkg

%prep
%goprep

%build
%gobuild -o %{gobuilddir}/bin/ccat %{goipath}

%install
%gopkginstall
install -m 0755 -vd                     %{buildroot}%{_bindir}
install -m 0755 -vp %{gobuilddir}/bin/* %{buildroot}%{_bindir}/

%if %{with check}
%check
%gocheck
%endif

%files
%license LICENSE
%doc README.md
%{_bindir}/*

%gopkgfiles

%changelog
* Sat Feb 22 04:37:27 UTC 2020 Breno Brand Fernandes <brandfbb@gmail.com> - 1.1.0-1
- Initial package


