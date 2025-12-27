%{?scl:%scl_package openssl}
%{!?scl:%global pkg_name %{name}}
%global _scl_prefix /opt/remi
%global _scl_vendor remi
%global scl_vendor remi
%global debug_package %{nil}

# For the curious:
# 0.9.5a soversion = 0
# 0.9.6  soversion = 1
# 0.9.6a soversion = 2
# 0.9.6c soversion = 3
# 0.9.7a soversion = 4
# 0.9.7ef soversion = 5
# 0.9.8ab soversion = 6
# 0.9.8g soversion = 7
# 0.9.8jk + EAP-FAST soversion = 8
# 1.0.0 soversion = 10
# 1.1.0 soversion = 1.1 (same as upstream although presence of some symbols
#                        depends on build configuration options)

# Arches on which we need to prevent arch conflicts on opensslconf.h, must
# also be handled in opensslconf-new.h.
%define multilib_arches %{ix86} ia64 %{mips} ppc ppc64 s390 s390x sparcv9 sparc64 %{_arch}

%global _performance_build 1

Summary: Compatibility version of the OpenSSL library
Name: php56-openssl
Version: 1.1.1w
Release: 1%{?dist}
Epoch: 1
Source: https://github.com/openssl/openssl/releases/download/OpenSSL_1_1_1w/openssl-%{version}.tar.gz
Source9: opensslconf-new.h
Source10: opensslconf-new-warning.h
# Build changes
Patch1: openssl-1.1.1-build.patch
Patch2: openssl-1.1.1-defaults.patch
Patch3: openssl-1.1.1-no-html.patch
Patch4: openssl-1.1.1-man-rename.patch

# Functionality changes
Patch31: openssl-1.1.1-conf-paths.patch
Patch32: openssl-1.1.1-version-add-engines.patch
Patch33: openssl-1.1.1-apps-dgst.patch
Patch38: openssl-1.1.1-no-weak-verify.patch
Patch40: openssl-1.1.1-disable-ssl3.patch
Patch41: openssl-1.1.1-system-cipherlist.patch
Patch45: openssl-1.1.1-weak-ciphers.patch
Patch46: openssl-1.1.1-seclevel.patch
Patch47: openssl-1.1.1-ts-sha256-default.patch
Patch49: openssl-1.1.1-evp-kdf.patch
Patch50: openssl-1.1.1-ssh-kdf.patch
Patch51: openssl-1.1.1-intel-cet.patch
Patch60: openssl-1.1.1-krb5-kdf.patch
Patch69: openssl-1.1.1-alpn-cb.patch
#Patch71: openssl-1.1.1-new-config-file.patch
# Backported fixes including security fixes
Patch52: openssl-1.1.1-s390x-update.patch

License: OpenSSL and ASL 2.0
URL: http://www.openssl.org/
%{?scl:Requires: %{scl}-runtime}
%{?scl:BuildRequires: %{scl}-runtime}
BuildRequires: make
BuildRequires: gcc
BuildRequires: coreutils, perl-interpreter, sed, zlib-devel, /usr/bin/cmp
BuildRequires: lksctp-tools-devel
BuildRequires: /usr/bin/rename
BuildRequires: /usr/bin/pod2man
BuildRequires: /usr/sbin/sysctl
BuildRequires: perl(Test::Harness), perl(Test::More), perl(Math::BigInt)
BuildRequires: perl(Module::Load::Conditional), perl(File::Temp)
BuildRequires: perl(Time::HiRes)
BuildRequires: perl(FindBin), perl(lib), perl(File::Compare), perl(File::Copy)
BuildRequires: scl-utils-build php56-build php56-runtime php56-scldevel


%description
The OpenSSL toolkit provides support for secure communications between
machines. OpenSSL includes a certificate management tool and shared
libraries which provide various cryptographic algorithms and
protocols.

%package devel
Summary: Files for development of applications which will use OpenSSL
Requires: %{?scl_prefix}%{pkg_name}%{?_isa} = %{epoch}:%{version}-%{release}
Requires: pkgconfig
Conflicts: openssl-devel


%description devel
OpenSSL is a toolkit for supporting cryptography. The openssl-devel
package contains include files needed to develop applications which
support various cryptographic algorithms and protocols.

%prep
%{?scl:scl enable %{scl} - << \EOF}
set -ex
%setup -q -n openssl-%{version}

%patch -P 1 -p1 -b .build   %{?_rawbuild}
%patch -P 2 -p1 -b .defaults
%patch -P 3 -p1 -b .no-html  %{?_rawbuild}
%patch -P 4 -p1 -b .man-rename

%patch -P 31 -p1 -b .conf-paths
%patch -P 32 -p1 -b .version-add-engines
%patch -P 33 -p1 -b .dgst
%patch -P 38 -p1 -b .no-weak-verify
%patch -P 40 -p1 -b .disable-ssl3
%patch -P 41 -p1 -b .system-cipherlist
%patch -P 45 -p1 -b .weak-ciphers
%patch -P 46 -p1 -b .seclevel
%patch -P 47 -p1 -b .ts-sha256-default
%patch -P 49 -p1 -b .evp-kdf
%patch -P 50 -p1 -b .ssh-kdf
%patch -P 51 -p1 -b .intel-cet
%patch -P 52 -p1 -b .s390x-update
%patch -P 60 -p1 -b .krb5-kdf
%patch -P 69 -p1 -b .alpn-cb
#%patch -P 71 -p1 -b .conf-new
%{?scl:EOF}


%build
%{?scl:scl enable %{scl} - << \EOF}
set -ex
# Figure out which flags we want to use.
# default
sslarch=%{_os}-%{_target_cpu}
%ifarch %ix86
sslarch=linux-elf
if ! echo %{_target} | grep -q i686 ; then
	sslflags="no-asm 386"
fi
%endif
%ifarch %{_arch}
sslflags=enable-ec_nistp_64_gcc_128
%endif
%ifarch sparcv9
sslarch=linux-sparcv9
sslflags=no-asm
%endif
%ifarch sparc64
sslarch=linux64-sparcv9
sslflags=no-asm
%endif
%ifarch alpha alphaev56 alphaev6 alphaev67
sslarch=linux-alpha-gcc
%endif
%ifarch s390 sh3eb sh4eb
sslarch="linux-generic32 -DB_ENDIAN"
%endif
%ifarch s390x
sslarch="linux64-s390x"
%endif
%ifarch %{arm}
sslarch=linux-armv4
%endif
%ifarch aarch64
sslarch=linux-aarch64
sslflags=enable-ec_nistp_64_gcc_128
%endif
%ifarch sh3 sh4
sslarch=linux-generic32
%endif
%ifarch ppc64 ppc64p7
sslarch=linux-ppc64
%endif
%ifarch ppc64le
sslarch="linux-ppc64le"
sslflags=enable-ec_nistp_64_gcc_128
%endif
%ifarch mips mipsel
sslarch="linux-mips32 -mips32r2"
%endif
%ifarch mips64 mips64el
sslarch="linux64-mips64 -mips64r2"
%endif
%ifarch mips64el
sslflags=enable-ec_nistp_64_gcc_128
%endif
%ifarch riscv64
sslarch=linux-generic64
%endif

# Add -Wa,--noexecstack here so that libcrypto's assembler modules will be
# marked as not requiring an executable stack.
# Also add -DPURIFY to make using valgrind with openssl easier as we do not
# want to depend on the uninitialized memory as a source of entropy anyway.
RPM_OPT_FLAGS="$RPM_OPT_FLAGS -Wa,--noexecstack -Wa,--generate-missing-build-notes=yes -DPURIFY $RPM_LD_FLAGS"

export HASHBANGPERL=/usr/bin/perl

# ia64, %{_arch}, ppc are OK by default
# Configure the build tree.  Override OpenSSL defaults with known-good defaults
# usable on all platforms.  The Configure script already knows to use -fPIC and
# RPM_OPT_FLAGS, so we can skip specifiying them here.
./Configure \
	--prefix=%{_prefix} --openssldir=%{_sysconfdir}/pki/tls ${sslflags} \
	--system-ciphers-file=%{_sysconfdir}/crypto-policies/back-ends/openssl.config \
	zlib enable-camellia enable-seed enable-rfc3779 enable-sctp \
	enable-cms enable-md2 enable-rc5 enable-ssl3 enable-ssl3-method \
	enable-weak-ssl-ciphers \
	shared  ${sslarch} $RPM_OPT_FLAGS '-DDEVRANDOM="\"/dev/urandom\""'

# Do not run this in a production package the FIPS symbols must be patched-in
#util/mkdef.pl crypto update

make all

# Clean up the .pc files
for i in libcrypto.pc libssl.pc openssl.pc ; do
  sed -i '/^Libs.private:/{s/-L[^ ]* //;s/-Wl[^ ]* //}' $i
done
%{?scl:EOF}


%check
%{?scl:scl enable %{scl} - << \EOF}
set -ex
# Verify that what was compiled actually works.


# Hack - either enable SCTP AUTH chunks in kernel or disable sctp for check
(sysctl net.sctp.addip_enable=1 && sysctl net.sctp.auth_enable=1) || \
(echo 'Failed to enable SCTP AUTH chunks, disabling SCTP for tests...' &&
 sed '/"zlib-dynamic" => "default",/a\ \ "sctp" => "default",' configdata.pm > configdata.pm.new && \
 touch -r configdata.pm configdata.pm.new && \
 mv -f configdata.pm.new configdata.pm)

# We must revert patch31 before tests otherwise they will fail
patch -p1 -R < %{PATCH31}

%define __provides_exclude_from %{_libdir}/openssl
%{?scl:EOF}


%install
%{?scl:scl enable %{scl} - << \EOF}
set -ex
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
# Install OpenSSL.
install -d $RPM_BUILD_ROOT{%{_bindir},%{_includedir},%{_libdir},%{_mandir},%{_libdir}/openssl,%{_pkgdocdir}}
%make_install


# Determine which arch opensslconf.h is going to try to #include.
basearch=%{_arch}
%ifarch %{ix86}
basearch=i386
%endif
%ifarch sparcv9
basearch=sparc
%endif
%ifarch sparc64
basearch=sparc64
%endif

# Next step of gradual disablement of SSL3.
# Make SSL3 disappear to newly built dependencies.
sed -i '/^\#ifndef OPENSSL_NO_SSL_TRACE/i\
#ifndef OPENSSL_NO_SSL3\
# define OPENSSL_NO_SSL3\
#endif' $RPM_BUILD_ROOT/%{_prefix}/include/openssl/opensslconf.h

%ifarch %{multilib_arches}
# Do an opensslconf.h switcheroo to avoid file conflicts on systems where you
# can have both a 32- and 64-bit version of the library, and they each need
# their own correct-but-different versions of opensslconf.h to be usable.
install -m644 %{SOURCE10} \
	$RPM_BUILD_ROOT/%{_prefix}/include/openssl/opensslconf-${basearch}.h
cat $RPM_BUILD_ROOT/%{_prefix}/include/openssl/opensslconf.h >> \
	$RPM_BUILD_ROOT/%{_prefix}/include/openssl/opensslconf-${basearch}.h
install -m644 %{SOURCE9} \
	$RPM_BUILD_ROOT/%{_prefix}/include/openssl/opensslconf.h
%endif


# Install compat config file
install -D -m 644 apps/openssl.cnf $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/openssl.cnf
%{?scl:EOF}


%files
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc FAQ NEWS README README.FIPS
%{_bindir}/openssl
%{_bindir}/c_rehash
%config(noreplace) %{_sysconfdir}/pki/tls/openssl.cnf
%{_sysconfdir}/pki/tls/ct_log_list.cnf
%{_sysconfdir}/pki/tls/ct_log_list.cnf.dist
%{_sysconfdir}/pki/tls/misc/CA.pl
%{_sysconfdir}/pki/tls/misc/tsget
%{_sysconfdir}/pki/tls/misc/tsget.pl
%{_sysconfdir}/pki/tls/openssl.cnf
%{_sysconfdir}/pki/tls/openssl.cnf.dist
%dir %{_sysconfdir}/pki/tls
%attr(0644,root,root) %{_sysconfdir}/pki/tls/openssl.cnf


%files devel
%doc CHANGES doc/dir-locals.example.el doc/openssl-c-indent.el
%{_prefix}/include/openssl
%attr(0755,root,root) %{_libdir}/*
%{_libdir}/*
%{_libdir}/engines-1.1/*
%{_mandir}/man3*/*
%{_mandir}/man1*/*
%{_mandir}/man5*/*
%{_mandir}/man7*/*
%{_libdir}/pkgconfig/*.pc

%post -p /sbin/ldconfig    
%postun -p /sbin/ldconfig

%files devel-debuginfo -f debuginfo.list

%files devel-debugsource -f debugsourcefiles.list


%changelog
* Thu Jan 25 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.1.1q-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Sun Jan 21 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.1.1q-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Thu Jul 20 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.1.1q-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Mon Feb 06 2023 Florian Weimer <fweimer@redhat.com> - 1:1.1.1q-4
- Backport upstream patch to fix C99 compatibility issue

* Thu Jan 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.1.1q-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Thu Jul 21 2022 Dmitry Belyavskiy <dbelyavs@redhat.com> - 1:1.1.1q-2
- Deprecate this package
  Resolves: rhbz#2108694

* Thu Jul 07 2022 Clemens Lang <cllang@redhat.com> - 1:1.1.1q-1
- Upgrade to 1.1.1q
  Resolves: CVE-2022-2097

* Thu Jun 30 2022 Clemens Lang <cllang@redhat.com> - 1:1.1.1p-1
- Upgrade to 1.1.1p
  Resolves: CVE-2022-2068
  Related: rhbz#2099975

* Mon Jun 13 2022 Clemens Lang <cllang@redhat.com> - 1:1.1.1o-1
- Upgrade to 1.1.1o
  Resolves: CVE-2022-1292
  Related: rhbz#2095817

* Thu Mar 24 2022 Clemens Lang <cllang@redhat.com> - 1:1.1.1n-1
- Upgrade to version 1.1.1n
  Resolves: CVE-2022-0778, rhbz#2064918

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.1.1l-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Mon Sep 20 2021 Sahana Prasad <sahana@redhat.com> - 1:1.1.1l-1
- Upgrade to version 1.1.1.l

* Mon Sep 20 2021 Miro Hrončok <mhroncok@redhat.com> - 1:1.1.1k-2
- Correctly name the arch-specific opensslconf header
- Fixes: rhbz#2004517

* Tue Aug 03 2021 Sahana Prasad <sahana@redhat.com> 1.1.1k-1
- Compat package rebased to latest upstream version 1.1.1k

* Thu Jul 22 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.1.1i-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.1.1i-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Dec 9 2020 Tomáš Mráz <tmraz@redhat.com> 1.1.1i-1
- Update to the 1.1.1i release fixing CVE-2020-1971

* Fri Oct 30 2020 Tomáš Mráz <tmraz@redhat.com> 1.1.1g-3
- Corrected wrong requires in the devel package

* Thu Sep 24 2020 Tomáš Mráz <tmraz@redhat.com> 1.1.1g-2
- Removed useless capi engine

* Fri Sep 11 2020 Tomáš Mráz <tmraz@redhat.com> 1.1.1g-1
- Compat package created
