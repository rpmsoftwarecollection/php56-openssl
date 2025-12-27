%{?scl:%scl_package openssl}
%{!?scl:%global pkg_name %{name}}
%global _scl_prefix /opt/remi
%global _scl_vendor remi
%global scl_vendor remi
#%global debug_package %{nil}

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

%package debug
Summary: Files for development of applications which will use OpenSSL
Requires: %{?scl_prefix}%{pkg_name}%{?_isa} = %{epoch}:%{version}-%{release}
Requires: pkgconfig
Conflicts: openssl-devel


%description debug
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

%files debug
/usr/lib/debug/.dwz/php56-openssl-1.1.1w-1%{dist}.%{_arch}
/usr/lib/debug/opt/remi/php56/root/usr/bin/openssl-1.1.1w-1%{dist}.%{_arch}.debug
/usr/lib/debug/opt/remi/php56/root/usr/lib64/engines-1.1/afalg.so-1.1.1w-1%{dist}.%{_arch}.debug
/usr/lib/debug/opt/remi/php56/root/usr/lib64/engines-1.1/capi.so-1.1.1w-1%{dist}.%{_arch}.debug
/usr/lib/debug/opt/remi/php56/root/usr/lib64/engines-1.1/padlock.so-1.1.1w-1%{dist}.%{_arch}.debug
/usr/lib/debug/opt/remi/php56/root/usr/lib64/libcrypto.so.1.1-1.1.1w-1%{dist}.%{_arch}.debug
/usr/lib/debug/opt/remi/php56/root/usr/lib64/libssl.so.1.1-1.1.1w-1%{dist}.%{_arch}.debug
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/app_rand.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/apps.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/apps.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/asn1pars.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/bf_prefix.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/ca.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/ciphers.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/cms.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/crl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/crl2p7.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/dgst.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/dhparam.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/dsa.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/dsaparam.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/ec.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/ecparam.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/engine.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/errstr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/gendsa.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/genpkey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/genrsa.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/nseq.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/ocsp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/openssl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/opt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/passwd.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/pkcs12.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/pkcs7.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/pkcs8.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/pkey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/pkeyparam.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/pkeyutl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/prime.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/progs.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/rand.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/rehash.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/req.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/rsa.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/rsautl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/s_apps.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/s_cb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/s_client.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/s_server.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/s_socket.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/s_time.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/sess_id.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/smime.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/speed.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/spkac.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/srp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/storeutl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/testdsa.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/testrsa.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/ts.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/verify.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/version.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/apps/x509.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/LPdir_unix.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/aes_cbc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/aes_cfb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/aes_core.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/aes_ecb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/aes_ige.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/aes_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/aes_misc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/aes_ofb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/aes_wrap.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/aesni-mb-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/aesni-sha1-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/aesni-sha256-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/aesni-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aes/vpaes-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/aria/aria.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_bitstr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_d2i_fp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_digest.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_dup.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_gentm.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_i2d_fp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_int.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_mbstr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_object.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_octet.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_print.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_sign.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_strex.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_strnid.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_time.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_type.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_utctm.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_utf8.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/a_verify.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/ameth_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/asn1_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/asn1_gen.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/asn1_item_list.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/asn1_item_list.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/asn1_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/asn1_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/asn1_par.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/asn_mime.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/asn_moid.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/asn_mstbl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/asn_pack.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/bio_asn1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/bio_ndef.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/charmap.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/d2i_pr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/d2i_pu.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/evp_asn1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/f_int.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/f_string.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/i2d_pr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/i2d_pu.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/n_pkey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/nsseq.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/p5_pbe.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/p5_pbev2.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/p5_scrypt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/p8_pkey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/standard_methods.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/t_bitst.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/t_pkey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/t_spki.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/tasn_dec.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/tasn_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/tasn_fre.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/tasn_new.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/tasn_prn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/tasn_scn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/tasn_typ.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/tasn_utl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/tbl_standard.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/x_algor.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/x_bignum.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/x_info.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/x_int64.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/x_long.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/x_pkey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/x_sig.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/x_spki.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/asn1/x_val.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/async/arch/async_null.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/async/arch/async_posix.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/async/arch/async_posix.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/async/arch/async_win.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/async/async.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/async/async_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/async/async_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/async/async_wait.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bf/bf_cfb64.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bf/bf_ecb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bf/bf_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bf/bf_ofb64.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bf/bf_pi.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bf/bf_skey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/b_addr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/b_dump.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/b_print.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/b_sock.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/b_sock2.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bf_buff.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bf_lbuf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bf_nbio.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bf_null.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bio_cb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bio_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bio_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bio_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bio_meth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bss_acpt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bss_bio.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bss_conn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bss_dgram.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bss_fd.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bss_file.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bss_log.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bss_mem.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bss_null.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bio/bss_sock.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/blake2/blake2_impl.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/blake2/blake2_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/blake2/blake2b.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/blake2/blake2s.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/blake2/m_blake2b.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/blake2/m_blake2s.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/asm/%{_arch}-gcc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_add.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_blind.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_const.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_ctx.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_depr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_dh.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_div.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_exp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_exp2.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_gcd.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_gf2m.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_intern.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_kron.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_mod.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_mont.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_mpi.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_mul.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_nist.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_prime.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_prime.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_print.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_rand.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_recp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_shift.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_sqr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_sqrt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_srp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_word.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/bn_x931p.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/rsaz-avx2.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/rsaz-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/rsaz_exp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/rsaz_exp.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/%{_arch}-gf2m.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/%{_arch}-mont.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/bn/%{_arch}-mont5.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/buffer/buf_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/buffer/buffer.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/buildinf.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/camellia/cmll-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/camellia/cmll_cfb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/camellia/cmll_ctr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/camellia/cmll_ecb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/camellia/cmll_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/camellia/cmll_misc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/camellia/cmll_ofb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cast/c_cfb64.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cast/c_ecb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cast/c_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cast/c_ofb64.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cast/c_skey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cast/cast_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cast/cast_s.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/chacha/chacha-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cmac/cm_ameth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cmac/cm_pmeth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cmac/cmac.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_asn1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_att.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_cd.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_dd.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_env.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_ess.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_io.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_kari.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_pwri.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_sd.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cms/cms_smime.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/comp/c_zlib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/comp/comp_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/comp/comp_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/comp/comp_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/conf/conf_api.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/conf/conf_def.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/conf/conf_def.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/conf/conf_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/conf/conf_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/conf/conf_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/conf/conf_mall.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/conf/conf_mod.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/conf/conf_sap.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/conf/conf_ssl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cpt_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cryptlib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ct/ct_b64.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ct/ct_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ct/ct_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ct/ct_log.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ct/ct_oct.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ct/ct_policy.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ct/ct_prn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ct/ct_sct.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ct/ct_sct_ctx.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ct/ct_vfy.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ct/ct_x509v3.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ctype.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/cversion.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/cbc_cksm.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/cbc_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/cfb64ede.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/cfb64enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/cfb_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/des_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/des_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/ecb3_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/ecb_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/fcrypt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/fcrypt_b.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/ncbc_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/ofb64ede.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/ofb64enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/ofb_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/pcbc_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/qud_cksm.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/rand_key.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/set_key.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/spr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/str2key.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/des/xcbc_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_ameth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_asn1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_check.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_depr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_gen.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_kdf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_key.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_meth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_pmeth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_prn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_rfc5114.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dh/dh_rfc7919.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_ameth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_asn1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_depr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_gen.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_key.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_meth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_ossl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_pmeth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_prn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_sign.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dsa/dsa_vrf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dso/dso_dl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dso/dso_dlfcn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dso/dso_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dso/dso_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dso/dso_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dso/dso_openssl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dso/dso_vms.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/dso/dso_win32.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ebcdic.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve25519.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/arch_32/arch_intrinsics.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/arch_32/f_impl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/arch_32/f_impl.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/curve448.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/curve448_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/curve448_tables.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/curve448utils.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/ed448.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/eddsa.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/f_generic.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/field.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/point_448.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/scalar.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/curve448/word.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec2_oct.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec2_smpl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_ameth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_asn1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_check.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_curve.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_cvt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_key.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_kmeth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_mult.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_oct.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_pmeth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ec_print.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecdh_kdf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecdh_ossl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecdsa_ossl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecdsa_sign.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecdsa_vrf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/eck_prn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecp_mont.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecp_nist.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecp_nistp224.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecp_nistp256.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecp_nistp521.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecp_nistputil.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecp_nistz256-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecp_nistz256.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecp_oct.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecp_smpl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/ecx_meth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ec/x25519-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_all.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_cnf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_ctrl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_dyn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_fat.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_init.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_list.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_openssl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_pkey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_rdrand.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/eng_table.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/tb_asnmth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/tb_cipher.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/tb_dh.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/tb_digest.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/tb_dsa.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/tb_eckey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/tb_pkmeth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/tb_rand.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/engine/tb_rsa.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/err/err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/err/err_all.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/err/err_prn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/bio_b64.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/bio_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/bio_md.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/bio_ok.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/c_allc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/c_alld.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/cmeth_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/digest.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_aes.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_aes_cbc_hmac_sha1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_aes_cbc_hmac_sha256.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_aria.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_bf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_camellia.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_cast.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_chacha20_poly1305.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_des.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_des3.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_idea.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_null.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_old.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_rc2.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_rc4.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_rc4_hmac_md5.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_rc5.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_seed.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_sm4.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/e_xcbc_d.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/encode.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/evp_cnf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/evp_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/evp_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/evp_key.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/evp_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/evp_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/evp_pbe.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/evp_pkey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/kdf_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/m_md2.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/m_md4.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/m_md5.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/m_md5_sha1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/m_mdc2.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/m_null.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/m_ripemd.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/m_sha1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/m_sha3.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/m_sigver.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/m_wp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/names.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/p5_crpt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/p5_crpt2.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/p_dec.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/p_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/p_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/p_open.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/p_seal.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/p_sign.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/p_verify.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/pbe_scrypt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/pkey_kdf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/pmeth_fn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/pmeth_gn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/evp/pmeth_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ex_data.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/getenv.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/hmac/hm_ameth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/hmac/hm_pmeth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/hmac/hmac.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/hmac/hmac_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/idea/i_cbc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/idea/i_cfb64.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/idea/i_ecb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/idea/i_ofb64.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/idea/i_skey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/init.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/kdf/hkdf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/kdf/kbkdf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/kdf/kdf_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/kdf/kdf_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/kdf/kdf_util.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/kdf/krb5kdf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/kdf/pbkdf2.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/kdf/scrypt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/kdf/sshkdf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/kdf/sskdf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/kdf/tls1_prf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/lhash/lh_stats.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/lhash/lhash.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/lhash/lhash_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/md2/md2_dgst.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/md2/md2_one.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/md4/md4_dgst.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/md4/md4_one.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/md5/md5-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/md5/md5_dgst.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/md5/md5_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/md5/md5_one.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/mdc2/mdc2_one.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/mdc2/mdc2dgst.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/mem.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/mem_dbg.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/mem_sec.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/modes/aesni-gcm-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/modes/cbc128.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/modes/ccm128.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/modes/cfb128.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/modes/ctr128.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/modes/cts128.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/modes/gcm128.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/modes/ghash-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/modes/modes_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/modes/ocb128.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/modes/ofb128.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/modes/wrap128.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/modes/xts128.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/o_dir.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/o_fips.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/o_fopen.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/o_init.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/o_str.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/o_time.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/objects/o_names.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/objects/obj_dat.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/objects/obj_dat.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/objects/obj_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/objects/obj_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/objects/obj_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/objects/obj_xref.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/objects/obj_xref.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ocsp/ocsp_asn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ocsp/ocsp_cl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ocsp/ocsp_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ocsp/ocsp_ext.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ocsp/ocsp_ht.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ocsp/ocsp_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ocsp/ocsp_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ocsp/ocsp_prn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ocsp/ocsp_srv.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ocsp/ocsp_vfy.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ocsp/v3_ocsp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pem/pem_all.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pem/pem_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pem/pem_info.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pem/pem_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pem/pem_oth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pem/pem_pk8.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pem/pem_pkey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pem/pem_sign.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pem/pem_x509.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pem/pem_xaux.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pem/pvkfmt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_add.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_asn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_attr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_crpt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_crt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_decr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_init.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_key.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_kiss.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_mutl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_npas.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_p8d.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_p8e.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_sbag.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/p12_utl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs12/pk12err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs7/bio_pk7.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs7/pk7_asn1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs7/pk7_attr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs7/pk7_doit.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs7/pk7_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs7/pk7_mime.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs7/pk7_smime.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/pkcs7/pkcs7err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/poly1305/poly1305-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/poly1305/poly1305.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/poly1305/poly1305_ameth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/poly1305/poly1305_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/poly1305/poly1305_pmeth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rand/drbg_ctr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rand/drbg_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rand/rand_egd.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rand/rand_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rand/rand_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rand/rand_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rand/rand_unix.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rand/rand_vms.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rand/rand_win.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rand/randfile.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rc2/rc2_cbc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rc2/rc2_ecb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rc2/rc2_skey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rc2/rc2cfb64.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rc2/rc2ofb64.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rc4/rc4-md5-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rc4/rc4-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rc5/rc5_ecb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rc5/rc5_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rc5/rc5_skey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rc5/rc5cfb64.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rc5/rc5ofb64.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ripemd/rmd_dgst.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ripemd/rmd_one.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_ameth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_asn1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_chk.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_crpt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_depr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_gen.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_meth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_mp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_none.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_oaep.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_ossl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_pk1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_pmeth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_prn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_pss.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_saos.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_sign.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_ssl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_x931.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/rsa/rsa_x931g.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/seed/seed.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/seed/seed_cbc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/seed/seed_cfb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/seed/seed_ecb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/seed/seed_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/seed/seed_ofb.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sha/keccak1600-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sha/sha1-mb-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sha/sha1-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sha/sha1_one.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sha/sha1dgst.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sha/sha256-mb-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sha/sha256-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sha/sha256.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sha/sha512-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sha/sha512.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sha/sha_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/siphash/siphash.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/siphash/siphash_ameth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/siphash/siphash_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/siphash/siphash_pmeth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sm2/sm2_crypt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sm2/sm2_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sm2/sm2_pmeth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sm2/sm2_sign.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sm3/m_sm3.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sm3/sm3.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/sm4/sm4.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/srp/srp_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/srp/srp_vfy.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/stack/stack.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/store/loader_file.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/store/store_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/store/store_init.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/store/store_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/store/store_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/store/store_register.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/store/store_strings.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/threads_none.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/threads_pthread.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/threads_win.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ts/ts_asn1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ts/ts_conf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ts/ts_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ts/ts_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ts/ts_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ts/ts_req_print.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ts/ts_req_utils.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ts/ts_rsp_print.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ts/ts_rsp_sign.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ts/ts_rsp_utils.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ts/ts_rsp_verify.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ts/ts_verify_ctx.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/txt_db/txt_db.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ui/ui_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ui/ui_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ui/ui_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ui/ui_null.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ui/ui_openssl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/ui/ui_util.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/uid.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/whrlpool/wp-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/whrlpool/wp_dgst.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/whrlpool/wp_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/by_dir.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/by_file.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/t_crl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/t_req.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/t_x509.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_att.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_cmp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_d2.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_def.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_ext.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_lu.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_meth.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_obj.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_r2x.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_req.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_set.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_trs.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_txt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_v3.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_vfy.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509_vpm.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509cset.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509name.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509rset.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509spki.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x509type.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x_all.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x_attrib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x_crl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x_exten.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x_name.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x_pubkey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x_req.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x_x509.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509/x_x509a.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/ext_dat.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/pcy_cache.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/pcy_data.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/pcy_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/pcy_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/pcy_map.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/pcy_node.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/pcy_tree.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/standard_exts.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_addr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_admis.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_admis.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_akey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_akeya.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_alt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_asid.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_bcons.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_bitst.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_conf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_cpols.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_crld.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_enum.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_extku.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_genn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_ia5.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_info.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_int.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_ncons.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_pci.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_pcia.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_pcons.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_pku.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_pmaps.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_prn.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_purp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_skey.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_sxnet.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_tlsf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3_utl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/x509v3/v3err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/crypto/%{_arch}cpuid.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/engines/e_afalg.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/engines/e_afalg.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/engines/e_afalg_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/engines/e_capi.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/engines/e_padlock-%{_arch}.s
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/engines/e_padlock.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/aria.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/asn1.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/async.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/bn.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/bn_dh.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/bn_srp.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/chacha.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/cryptlib.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/ctype.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/ec.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/engine.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/err.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/evp.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/lhash.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/md32_common.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/objects.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/poly1305.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/rand.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/sha.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/siphash.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/sm2.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/sm3.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/sm4.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/store.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/crypto/x509.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/internal/bio.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/internal/comp.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/internal/conf.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/internal/constant_time.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/internal/cryptlib.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/internal/dane.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/internal/dso.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/internal/o_dir.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/internal/refcount.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/internal/sslconf.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/aes.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/asn1.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/asn1err.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/asn1t.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/async.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/asyncerr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/bio.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/bioerr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/blowfish.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/bn.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/bnerr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/buffer.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/buffererr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/camellia.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/cast.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/cmac.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/cms.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/cmserr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/comp.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/comperr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/conf.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/conf_api.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/conferr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/crypto.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/cryptoerr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/ct.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/cterr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/des.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/dh.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/dherr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/dsa.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/dsaerr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/ec.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/ecerr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/engine.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/engineerr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/err.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/evp.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/evperr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/hmac.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/idea.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/kdf.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/kdferr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/lhash.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/md2.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/md4.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/md5.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/mdc2.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/modes.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/objects.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/objectserr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/ocsp.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/ocsperr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/ossl_typ.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/pem.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/pemerr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/pkcs12.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/pkcs12err.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/pkcs7.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/pkcs7err.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/rand.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/rand_drbg.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/randerr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/rc2.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/rc4.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/rc5.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/ripemd.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/rsa.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/rsaerr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/safestack.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/seed.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/sha.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/srp.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/srtp.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/ssl.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/sslerr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/stack.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/store.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/storeerr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/tls1.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/ts.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/tserr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/txt_db.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/ui.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/uierr.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/whrlpool.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/x509.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/x509_vfy.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/x509err.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/x509v3.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/include/openssl/x509v3err.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/bio_ssl.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/d1_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/d1_msg.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/d1_srtp.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/methods.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/packet.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/packet_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/pqueue.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/record/dtls1_bitmap.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/record/rec_layer_d1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/record/rec_layer_s3.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/record/record.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/record/record_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/record/ssl3_buffer.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/record/ssl3_record.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/record/ssl3_record_tls13.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/s3_cbc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/s3_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/s3_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/s3_msg.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_asn1.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_cert.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_cert_table.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_ciph.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_conf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_err.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_init.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_mcnf.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_rsa.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_sess.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_stat.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_txt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/ssl_utst.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/statem/extensions.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/statem/extensions_clnt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/statem/extensions_cust.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/statem/extensions_srvr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/statem/statem.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/statem/statem.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/statem/statem_clnt.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/statem/statem_dtls.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/statem/statem_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/statem/statem_local.h
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/statem/statem_srvr.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/t1_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/t1_lib.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/t1_trce.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/tls13_enc.c
/usr/src/debug/php56-openssl-1.1.1w-1%{dist}.%{_arch}/ssl/tls_srp.c


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
