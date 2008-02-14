%define db_version 4.5
%define dbxml_version 2.3.10
%define libdbxml %mklibname dbxml 2.3

%define with_java 1
%{?_without_java: %{expand: %%global with_java 0}}

Name: dbxml
Version: %{dbxml_version}
Release: %mkrel 1
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Summary: Berkeley DB XML
URL: http://www.sleepycat.com/products/xml.shtml
License:  Other License(s), see package, BSD
Source0: dbxml-%{dbxml_version}.tar.gz
Patch0: patch.%{dbxml_version}.1
Patch1: patch.%{dbxml_version}.2
Patch2: patch.%{dbxml_version}.3
Patch3: patch.%{dbxml_version}.4
Patch4: patch.%{dbxml_version}.5
Patch5: patch.%{dbxml_version}.6
Patch6: patch.%{dbxml_version}.7
Patch7: patch.%{dbxml_version}.8
Patch8: patch.%{dbxml_version}.9
Patch9: dbxml-2.3.10-dbxml-install.patch
BuildRequires: db%{db_version}-devel
BuildRequires: xerces-c-devel 
BuildRequires: libicu-devel 
BuildRequires: update-alternatives
%if %with_java
BuildRequires: jpackage-utils
BuildRequires: java-devel >= 1.7.0
BuildRequires: %{_lib}dbjava%{db_version}
%endif

%description
This is the Berkeley DB XML from Sleepycat Software.

#------------------------------------------------------------------------

%package -n %libdbxml
Summary: Berkeley DB XML
Group: Development/Libraries

%description -n %libdbxml
Berkeley DB XML

%files -n %libdbxml
%defattr(-,root,root)
%{_libdir}/libdbxml-2.3.so
%{_libdir}/libdbxml-2.3.la       

#------------------------------------------------------------------------

%if %with_java

%package -n dbxml-java
Summary: Berkeley DB XML Java
Group: Development/Libraries

%description -n dbxml-java
Berkeley DB XML Java

%files -n dbxml-java
%defattr(-,root,root)
%{_javadir}/dbxml.jar
%{_libdir}/libdbxml_java-2.3.so
%{_libdir}/libdbxml_java-2.3_g.so

%endif

#------------------------------------------------------------------------

%define libxqilla %mklibname xqilla 1
%define libxqilla_devel %mklibname xqilla -d

%package -n %{libxqilla}
Summary: Xqilla library
Group: Development/Libraries

%description  -n %{libxqilla}
Xqilla library

%files -n  %{libxqilla}
%defattr(0755,root,root)
%{_libdir}/libxqilla.so.*

%package -n %{libxqilla_devel}
Summary: Xqilla devel library
Group: Development/Libraries

%description  -n %{libxqilla_devel}
Xqilla devel library

%files -n  %{libxqilla_devel}
%defattr(0755,root,root)
%{_libdir}/libxqilla.so
%{_libdir}/libxqilla.la
%{_includedir}/xqilla

#------------------------------------------------------------------------

%package utils
Summary: Berkeley DB XML
Group: Development/Libraries
Requires: %libdbxml = %{version}

%description utils
This is the Berkeley DB XML from Sleepycat Software.

%files utils
%defattr(0755,root,root)
%_bindir/*

#------------------------------------------------------------------------

%package -n %libdbxml-devel
Summary: Berkeley DB XML development libraries
Group: Development/Libraries
Requires: xerces-c-devel
Requires: db%{db_version}-devel
Requires: libstdc++-devel 
Requires: %libdbxml = %version
%if %with_java
Requires: dbxml-java = %version
%endif
Provides: dbxml-devel = %version
Provides: libdbxml-devel = %version

%description -n %libdbxml-devel
These are development libraries and headers for the Berkeley DB XML
from Sleepycat Software.

%files -n %libdbxml-devel 
%defattr(-,root,root)
%{_includedir}/dbxml
%{_libdir}/libdbxml-2.so       
%{_libdir}/libdbxml.so       
%if %with_java
%{_libdir}/libdbxml_java-2.so  
%{_libdir}/libdbxml_java.so
%{_libdir}/libdbxml_java-2.3.la
%endif

#------------------------------------------------------------------------

%package doc
Summary: Berkeley DB XML development libraries
Group: Development/Libraries

%description doc
These are development libraries and headers for the Berkeley DB XML
from Sleepycat Software.

%files doc
%defattr(-,root,root)
%doc %{_defaultdocdir}/dbxml

#------------------------------------------------------------------------

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1 
%patch5 -p1 
%patch6 -p1 
%patch7 -p1 
%patch8 -p1
%patch9 -p1 -b .install 

%build
%if %with_java
    source %_sysconfdir/java/java.conf
%endif

CFLAGS="%{optflags} -fPIC "
CXXFLAGS="%{optflags} -fPIC"
CPPFLAGS="-I%_includedir/db4" 
export CFLAGS CXXFLAGS CPPFLAGS

#################  build xqilla

mkdir -p xqilla/build_unix
pushd xqilla/build_unix
	
	../configure \
    	--with-xerces=%_prefix \
		--libdir=%_libdir \
		--prefix=%_prefix \
		--disable-static

	%make && make DESTDIR=%buildroot install
popd


#################  build dbxml

pushd dbxml/dist
%if %with_java
    export ADDITIONAL_CLASSPATH=":%_datadir/java/db-%{db_version}.jar"
%endif
    ./s_config
    ./s_all
    %if "%_lib" != "lib"
        sed -i "s,/lib/,/lib64/,g" configure
    %endif
    
    CONFIGURE_TOP=${PWD}

    cd ../build_unix

    %configure2_5x \
%if %with_java
    --enable-java \
%else
    --disable-java \
%endif
    --with-xerces=%_prefix \
	--with-xqilla=%buildroot/%_prefix \
    --with-berkeleydb=%_prefix \
	--disable-static

    make 
popd

%install
rm -rf %buildroot
for name in xqilla/build_unix dbxml/build_unix; do
    pushd ${name}
        make DESTDIR=%buildroot install
    popd
done

%if %with_java
# Move jar to proper place
mkdir -p %buildroot%_datadir/java
mv %buildroot%_libdir/dbxml.jar %buildroot%_datadir/java/dbxml.jar
%endif

# install docs
mkdir -p %buildroot%_defaultdocdir/dbxml
cp -a dbxml/docs/* %buildroot%_defaultdocdir/dbxml

%clean
rm -rf $RPM_BUILD_ROOT

