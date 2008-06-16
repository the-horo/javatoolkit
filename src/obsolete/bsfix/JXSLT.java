/*
 * Copyright (C) 2004, Jan Brinkmann <lucky@the-luckyduck.de>
 * Copyright (c) 2004, Karl Trygve Kalleberg <karltk@gentoo.org>
 * Copyright (c) 2004, Thomas Matthijs <axxo@gentoo.org>
 * Copyright (c) 2004, Gentoo Foundation
 * 
 * Licensed under the GNU General Public License, v2
 *
 */

import javax.xml.transform.Result;
import javax.xml.transform.Source;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;
import java.io.*;

public class JXSLT
{
    public static void printHelp()
    {
        System.err
                .println("Usage: java JXSLT ( -v <version> || -s <version> -t <version> ) -x <build.xslt> -i <oldbuild.xml> -o <newbuild.xml> ");
    }

    public static void main(String[] args)
    {
        // check if there are enough options given
        if (args.length <= 8)
        {
            System.err.println("missing options");
            printHelp();
            System.exit(1);
        }

        // detailed parsing of command line arguments
        File oldXmlFile = null, newXmlFile = null, xsltFile = null;
        String source = null, target = null;
        int i = 0;
        while (i < args.length)
        {
            boolean match = false;
            String[] options = {
                    "-v", "--version", "-s", "--source", "-t", "--target", "-x", "--xsltsource", "-i", "--oldxml", "-o", "--newxml"
            };
            
            if (args[i].substring(0, 1).equals("-"))
            {
                if (args[i+1].substring(0, 1).equals("-")) {
                    System.err.println("missing argument for '"+args[i]+"'");
                    printHelp();
                    System.exit(1);
                }
                
                int j = 0;
                while (j < options.length)
                {
                    if (options[j].equals(args[i]))
                    {
                        match = true;
                        break;
                    }
                    ++j;
                }

                if (match != true)
                {
                    System.err.println("invalid option '" + args[i] + "'");
                    printHelp();
                    System.exit(1);
                }
            } 

            if (args[i].equalsIgnoreCase("-v") || args[i].equalsIgnoreCase("--version"))
            {
                target = source = args[i + 1];
            } else if (args[i].equalsIgnoreCase("-s") || args[i].equalsIgnoreCase("--source")) 
			{
				source = args[i + 1];
			}  else if (args[i].equalsIgnoreCase("-t") || args[i].equalsIgnoreCase("--target")) 
			{
				target = args[i + 1];
			} else if (args[i].equalsIgnoreCase("-x")
                    || args[i].equalsIgnoreCase("--xsltsource"))
            {
                xsltFile = new File(args[i + 1]);
            } else if (args[i].equalsIgnoreCase("-i") || args[i].equalsIgnoreCase("--oldxml"))
            {
                oldXmlFile = new File(args[i + 1]);
            } else if (args[i].equalsIgnoreCase("-o") || args[i].equalsIgnoreCase("--newxml"))
            {
                newXmlFile = new File(args[i + 1]);
            }

            ++i;
        }
        
        // check if files exist
        Source xmlSource = null, xsltSource = null;
        if (oldXmlFile.exists())
        {
            xmlSource = new StreamSource(oldXmlFile);
        } else
        {
            System.out.println("xml sourcefile doesn't exist");
            System.exit(1);
        }

        if (xsltFile.exists())
        {
            xsltSource = new StreamSource(xsltFile);
        } else
        {
            System.out.println("xslt sourcefile doesn't exist");
            System.exit(1);
        }
        Result result = new StreamResult(newXmlFile);

        // create a new transformer and perform a transformation
        TransformerFactory transFact = TransformerFactory.newInstance();
        Transformer trans = null;
        try
        {
            trans = transFact.newTransformer(xsltSource);
            trans.setParameter("source", source);
            trans.setParameter("target", target);
            trans.transform(xmlSource, result);
            System.out.println(oldXmlFile + " transformed to " + newXmlFile);
			System.exit(0);
        } catch (TransformerConfigurationException e)
        {
            e.printStackTrace();
        } catch (TransformerException e)
        {
            e.printStackTrace();
        }
    }
}
