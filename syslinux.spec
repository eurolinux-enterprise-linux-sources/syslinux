Summary: Simple kernel loader which boots from a FAT filesystem
Name: syslinux
Version: 4.05
%define tarball_version 4.05
Release: 15%{?dist}
License: GPLv2+
Group: Applications/System
URL: http://syslinux.zytor.com/wiki/index.php/The_Syslinux_Project
Source0: http://www.kernel.org/pub/linux/utils/boot/syslinux/%{name}-%{tarball_version}.tar.bz2
ExclusiveArch: x86_64
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: nasm >= 0.98.38-1, perl, netpbm-progs, git
BuildRequires: libuuid-devel
BuildRequires: /usr/include/gnu/stubs-32.h
BuildRequires: cpio, findutils
%ifarch x86_64
Requires: mtools, libc.so.6()(64bit), libuuid
%endif

Patch0001: syslinux-isohybrid-fix-mbr.patch
Patch0002: syslinux-4.05-avoid-ext2_fs.h.patch
Patch0003: syslinux-4.05-man-pages.patch
Patch0006: 0003-Fixes-for-problems-discovered-by-coverity-scan.-8120.patch
Patch0007: 0004-Make-some-more-mingw-paths-work.patch
Patch0008: 0001-Don-t-use-strict-aliasing-because-not-everything-her.patch
Patch0009: 0001-relocs-Move-stop-to-the-end.patch
Patch0010: 0005-Save-Dell-BIOS-chunk-in-PXELINUX.patch

%description
SYSLINUX is a suite of bootloaders, currently supporting DOS FAT
filesystems, Linux ext2/ext3 filesystems (EXTLINUX), PXE network boots
(PXELINUX), or ISO 9660 CD-ROMs (ISOLINUX).

%package perl
Summary: Syslinux tools written in perl
Group: Applications/System

%description perl
Syslinux tools written in perl

%package extlinux
Summary: The EXTLINUX bootloader, for booting the local system.
Group: System/Boot
Requires: syslinux

%description extlinux
The EXTLINUX bootloader, for booting the local system, as well as all
the SYSLINUX/PXELINUX modules in /boot.

%package devel
Summary: Headers and libraries for syslinux development.
Group: Development/Libraries

%description devel
Headers and libraries for syslinux development.

%package tftpboot
Summary: SYSLINUX modules in /var/lib/tftpboot, available for network booting
Group: Applications/Internet
BuildArch: noarch

%description tftpboot
All the SYSLINUX/PXELINUX modules directly available for network
booting in the /var/lib/tftpboot directory.

%prep
%setup -q -n syslinux-%{tarball_version}
git init
git config user.email "nobody@example.com"
git config user.name "RHEL Ninjas"
git add .
git commit -a -q -m "%{version} baseline."
git am %{patches} </dev/null

%build
CFLAGS="-Werror -Wno-unused -finline-limit=2000"
export CFLAGS

# If you make clean here, we lose the provided syslinux.exe
find . -name '*.exe' | cpio -H newc --quiet -o -F %{_tmppath}/%{name}-%{version}-%{release}.cpio
make clean
# There's an x86_64 image here that shouldn't be, and it makes i686 builds fail.
rm -vf diag/geodsp/mk-lba-img
make all
make installer
make -C sample tidy

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_prefix}/lib/syslinux
mkdir -p %{buildroot}%{_includedir}
cat %{_tmppath}/%{name}-%{version}-%{release}.cpio | cpio -di
make install-all \
	INSTALLROOT=%{buildroot} BINDIR=%{_bindir} SBINDIR=%{_sbindir} \
       	LIBDIR=%{_prefix}/lib DATADIR=%{_datadir} \
	MANDIR=%{_mandir} INCDIR=%{_includedir} \
	TFTPBOOT=/var/lib/tftpboot EXTLINUXDIR=/boot/extlinux

mkdir -p %{buildroot}/%{_docdir}/%{name}-%{version}/sample
install -m 644 sample/sample.* %{buildroot}/%{_docdir}/%{name}-%{version}/sample/
mkdir -p %{buildroot}/etc
( cd %{buildroot}/etc && ln -s ../boot/extlinux/extlinux.conf . )

# don't ship libsyslinux, at least, not for now
rm -f %{buildroot}%{_prefix}/lib/libsyslinux*
rm -f %{buildroot}%{_includedir}/syslinux.h

mkdir -p %{buildroot}/%{_libdir}/syslinux/com32/
mv %{buildroot}/%{_datadir}/syslinux/com32/*.a %{buildroot}/%{_libdir}/syslinux/com32/

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc NEWS README* COPYING 
%doc doc/* 
%doc sample
%{_mandir}/man1/gethostip*
%{_mandir}/man1/isohybrid*
%{_mandir}/man1/memdiskfind*
%{_mandir}/man1/syslinux*
%{_bindir}/gethostip
%{_bindir}/isohybrid
%{_bindir}/memdiskfind
%{_bindir}/syslinux
%dir %{_datadir}/syslinux
%dir %{_datadir}/syslinux/dosutil
%{_datadir}/syslinux/dosutil/*
%dir %{_datadir}/syslinux/diag
%{_datadir}/syslinux/diag/*
%{_datadir}/syslinux/memdisk
%{_datadir}/syslinux/*.com
%{_datadir}/syslinux/*.exe
%{_datadir}/syslinux/*.c32
%{_datadir}/syslinux/*.bin
%{_datadir}/syslinux/*.0

%files perl
%defattr(-,root,root)
%{_mandir}/man1/lss16toppm*
%{_mandir}/man1/ppmtolss16*
%{_mandir}/man1/syslinux2ansi*
%{_bindir}/keytab-lilo
%{_bindir}/lss16toppm
%{_bindir}/md5pass
%{_bindir}/mkdiskimage
%{_bindir}/ppmtolss16
%{_bindir}/pxelinux-options
%{_bindir}/sha1pass
%{_bindir}/syslinux2ansi
%{_bindir}/isohybrid.pl

%files extlinux
%defattr(-,root,root)
%{_sbindir}/extlinux
%{_mandir}/man1/extlinux*
%config /etc/extlinux.conf
/boot/extlinux

%files devel
%defattr(-,root,root)
%dir %{_datadir}/syslinux/com32
%{_datadir}/syslinux/com32
%dir %{_libdir}/syslinux/com32
%{_libdir}/syslinux/com32/*

%files tftpboot
%defattr(-,root,root)
%{_sharedstatedir}/tftpboot

%post extlinux
# If we have a /boot/extlinux.conf file, assume extlinux is our bootloader
# and update it.
if [ -f /boot/extlinux/extlinux.conf ]; then \
	extlinux --update /boot/extlinux ; \
elif [ -f /boot/extlinux.conf ]; then \
	mkdir -p /boot/extlinux && \
	mv /boot/extlinux.conf /boot/extlinux/extlinux.conf && \
	extlinux --update /boot/extlinux ; \
fi

%changelog
* Thu Sep 20 2018 Javier Martinez Canillas <javierm@redhat.com> - 4.05-15
- Drop x86_64 ExclusiveArch for tftpboot subpackage.
  Resolves: rhbz#1588578

* Wed Sep 12 2018 Javier Martinez Canillas <javierm@redhat.com> - 4.05-14
- Make tftpboot package noarch
  Resolves: rhbz#1588578

* Tue May 10 2016 Peter Jones <pjones@redhat.com> - - 4.05-13
- Try to work around firmware bugs in the PXE stack.
  Resolves: rhbz#1254615

* Fri Sep 26 2014 Peter Jones <pjones@redhat.com> - 4.05-12
- Toolchain changes between when this originally got built and 4.05-9 means
  4.05-9 - 4.05-11 don't actually work.
  Related: rhbz#1085434

* Tue Sep 23 2014 Peter Jones <pjones@redhat.com> - 4.05-11
- Fix some rpmdiff problems.
  Related: rhbz#1085434

* Tue Sep 23 2014 Peter Jones <pjones@redhat.com> - 4.05-10
- Fix some aliasing errors rpmdiff complains about.
  Related: rhbz#1085434

* Tue Sep 02 2014 Peter Jones <pjones@redhat.com> - 4.05-9
- Try harder to build everything correctly.
  Resolves: rhbz#1085434

* Thu Feb 27 2014 David Cantrell <dcantrell@redhat.com> - 4.05-8
- Only build for x86_64
  Resolves: rhbz#1070659

* Mon Jan 20 2014 Peter Jones <pjones@redhat.com> - 4.05-7
- Improve documentation.
  Resolves: rhbz#948852

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 4.05-6
- Mass rebuild 2013-12-27

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.05-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Aug 06 2012 Peter Jones <pjones@redhat.com> - 4.05-4
- Fix build problem from kernel-headers' removeal of ext2_fs.h
  (fix backported from as-yet-unreleased upstream version.)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.05-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Apr 18 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 4.05-2
- Remove old Obsoletes/Provides for syslinux-devel as such a subpkg
  was introduced with 3.83-2 (#756733).

* Wed Feb 15 2012 Matthew Garrett <mjg@redhat.com> - 4.05-1
- New upstream release
- syslinux-isohybrid-fix-mbr.patch: generate a full MBR for UEFI images

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.02-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Aug 24 2011 Matthew Garrett <mjg@redhat.com> - 4.02-5
- Add support for building Mac and GPT bootable hybrid images

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.02-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Aug 20 2010 Matt Domsch <mdomsch@fedoraproject.org> - 4.02-2
- add perl subpackage, move perl apps there

* Fri Aug 06 2010 Peter Jones <pjones@redhat.com> - 4.02-2
- Split out extlinux and tftpboot.
- remove duplicate syslinux/com32/ left in base package after 3.83-2

* Thu Aug 05 2010 Peter Jones <pjones@redhat.com> - 4.02-1
- Update to 4.02
