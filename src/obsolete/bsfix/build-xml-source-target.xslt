<?xml version="1.0"?>
	<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="xml" indent="yes" />
	<xsl:param name="target" />
	<xsl:param name="source" />

	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="javac|xjavac|javac.preset">
		<xsl:copy>
			<xsl:attribute name="target">
				<xsl:value-of select="$target"/>
			</xsl:attribute>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="javac|xjavac|javac.preset|javadoc">
		<xsl:copy>
			<xsl:attribute name="source">
				<xsl:value-of select="$source"/>
			</xsl:attribute>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>
</xsl:stylesheet>
