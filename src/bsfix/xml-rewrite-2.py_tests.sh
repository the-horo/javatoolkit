#!/bin/sh
files=""
JAVA_PKG_BSFIX_TARGET_TAGS=${JAVA_PKG_BSFIX_TARGET_TAGS:-"javac xjavac javac.preset"}
JAVA_PKG_BSFIX_SOURCE_TAGS=${JAVA_PKG_BSFIX_SOURCE_TAGS:-"javadoc javac xjavac javac.preset"}

want_source="java-1.4"
want_target="java-1.5"
rpath="./xmls"

for i in $(ls $rpath/b*);
do
	files=" $files -f $i"
done

clean(){
 rm -rf $rpath
 cp -rf $rpath.sav $rpath
}

old() {
	xml-rewrite-2.py ${files} \
	-c -e ${JAVA_PKG_BSFIX_SOURCE_TAGS// / -e } \
	-a source -v ${want_source} ${output} 
	xml-rewrite-2.py ${files} \
	-c -e ${JAVA_PKG_BSFIX_TARGET_TAGS// / -e } \
	-a target -v ${want_target} ${output}  
}

new(){
	/home/kiorky/prog/svn/gentoo.org/gentoo-java-overlays/projects/javatoolkit/trunk/src/bsfix/xml-rewrite-2.py ${files} \
	-c --source-element ${JAVA_PKG_BSFIX_SOURCE_TAGS// / -e } \
	--source-attribute source --source-value ${want_source} \
	--target-element   ${JAVA_PKG_BSFIX_TARGET_TAGS// / -e }  \
	--target-attribute target --target-value ${want_target} \
	${output}  
}

clean
echo  "_________________time old"
time old|grep -v "ewrit"

clean
echo  "_________________time new"
time new|grep -v "ewrit"  

