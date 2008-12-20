%define _disable_ld_no_undefined	1
%define _disable_ld_as_needed		1

%define db_version 4.6
%define dbxml_version 2.4.11
%define libdbxml %mklibname dbxml 2.4
%define libdbxmldev %mklibname dbxml -d

%define with_java 1
%{?_without_java: %{expand: %%global with_java 0}}

%define enable_debug 1
%{?_enable_debug: %{expand: %%global enable_debug 1}}

Name: dbxml
Version: %{dbxml_version}
Release: %mkrel 3
Group: Databases
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Summary: Berkeley DB XML
URL: http://www.oracle.com/database/berkeley-db/xml/index.html
License:  Other License(s), see package, BSD
Source0: dbxml-%{dbxml_version}.tar.gz
Patch0: dbxml-2.3.10-dbxml-install.patch
BuildRequires: db%{db_version}-devel
BuildRequires: libicu-devel 
BuildRequires: update-alternatives
BuildRequires: xerces-c-devel >= 2.8.0
BuildRequires: libxqilla-devel >= 2.1.1
BuildRequires: swig
%if %with_java
BuildRequires: jpackage-utils
BuildRequires: java-devel >= 1.6.0
BuildRequires: %{_lib}dbjava%{db_version}
%endif

%description
This is the Berkeley DB XML from Sleepycat Software.

#------------------------------------------------------------------------

%package -n %libdbxml
Summary: Berkeley DB XML
Group: System/Libraries

%description -n %libdbxml
Berkeley DB XML

%files -n %libdbxml
%defattr(-,root,root)
%{_libdir}/libdbxml-2.4.so
%{_libdir}/libdbxml-2.4.la       

#------------------------------------------------------------------------

%if %with_java

%package -n dbxml-java
Summary: Berkeley DB XML Java
Group: System/Libraries

%description -n dbxml-java
Berkeley DB XML Java

%files -n dbxml-java
%defattr(-,root,root)
%{_javadir}/dbxml.jar
%{_libdir}/libdbxml_java-2.4.so
%{_libdir}/libdbxml_java-2.4_g.so

%endif

#------------------------------------------------------------------------

%package utils
Summary: Berkeley DB XML
Group: Databases
Requires: %libdbxml = %{version}

%description utils
This is the Berkeley DB XML from Sleepycat Software.

%files utils
%defattr(0755,root,root)
%_bindir/*

#------------------------------------------------------------------------

%package -n %libdbxmldev
Summary: Berkeley DB XML development libraries
Group: Development/Databases
Requires: xerces-c-devel
Requires: db%{db_version}-devel
Requires: libstdc++-devel 
Requires: %libdbxml = %version
%if %with_java
Requires: dbxml-java = %version
%endif
Provides: dbxml-devel = %version
Provides: libdbxml-devel = %version
Obsoletes: %{_lib}dbxml2.3-devel

%description -n %libdbxmldev
These are development libraries and headers for the Berkeley DB XML
from Sleepycat Software.

%files -n %libdbxmldev 
%defattr(-,root,root)
%{_includedir}/dbxml
%{_libdir}/libdbxml-2.so       
%{_libdir}/libdbxml.so       
%if %with_java
%{_libdir}/libdbxml_java-2.so  
%{_libdir}/libdbxml_java.so
%{_libdir}/libdbxml_java-2.4.la
%endif

#------------------------------------------------------------------------

%package doc
Summary: Berkeley DB XML development libraries
Group: Databases

%description doc
These are development libraries and headers for the Berkeley DB XML
from Sleepycat Software.

%files doc
%defattr(-,root,root)
%doc %{_defaultdocdir}/dbxml

#------------------------------------------------------------------------

%prep
%setup -q
%patch0 -p1 -b .install 

%build
%if %with_java
    source %_sysconfdir/java/java.conf
%endif

CPPFLAGS="-I%_includedir/db4 -DPIC -fPIC" 
export CPPFLAGS

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
	--with-xqilla=%_prefix \
    --with-berkeleydb=%_prefix \
	%if %{enable_debug}
		--enable-debug \
	%endif
	--disable-static

    make 
popd

%install
rm -rf %buildroot
pushd dbxml/build_unix
	make DESTDIR=%buildroot install
popd

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

