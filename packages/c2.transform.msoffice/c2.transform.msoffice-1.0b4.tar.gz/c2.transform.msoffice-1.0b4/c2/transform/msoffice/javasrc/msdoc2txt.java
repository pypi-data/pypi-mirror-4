import java.io.*;
import org.apache.poi.openxml4j.opc.PackageProperties;
import org.apache.poi.extractor.ExtractorFactory;
import org.apache.poi.POITextExtractor;
import org.apache.xmlbeans.XmlException;
import org.apache.poi.openxml4j.exceptions.OpenXML4JException;
import org.apache.poi.openxml4j.exceptions.InvalidFormatException;
import org.apache.poi.POIOLE2TextExtractor;
import org.apache.poi.POIXMLTextExtractor;
import org.apache.poi.POITextExtractor;

import org.apache.poi.hdgf.extractor.VisioTextExtractor;
import org.apache.poi.hwpf.extractor.WordExtractor;
import org.apache.poi.hssf.extractor.ExcelExtractor;
import org.apache.poi.hslf.extractor.PowerPointExtractor;
import org.apache.poi.xslf.extractor.XSLFPowerPointExtractor;
import org.apache.poi.hwpf.*;
import org.apache.poi.hwpf.extractor.*;
import org.apache.poi.poifs.filesystem.*;
import org.apache.poi.hwpf.*;
import org.apache.poi.hwpf.extractor.*;
import org.apache.poi.poifs.filesystem.POIFSFileSystem;
import java.util.Iterator;
import org.apache.poi.openxml4j.opc.OPCPackage;
import org.apache.poi.POIXMLDocument;

import org.apache.poi.xslf.XSLFSlideShow;
import org.apache.poi.xslf.extractor.XSLFPowerPointExtractor;
import org.apache.poi.xssf.extractor.XSSFExcelExtractor;
import org.apache.poi.xssf.usermodel.XSSFRelation;
import org.apache.poi.xwpf.extractor.XWPFWordExtractor;
import org.apache.poi.xwpf.usermodel.XWPFRelation;
import org.apache.poi.openxml4j.opc.PackagePart;
import org.apache.poi.openxml4j.opc.PackageRelationshipCollection;
import org.apache.poi.POIDocument;
import org.apache.poi.hwpf.HWPFDocument;
import org.apache.poi.hslf.HSLFSlideShow;
import org.apache.poi.hdgf.HDGFDiagram;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;
import org.apache.poi.hpsf.SummaryInformation;
import org.apache.poi.xslf.XSLFSlideShow;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.POIXMLDocument;
import org.apache.poi.POIXMLProperties;
import org.apache.poi.POIXMLProperties.CoreProperties;

public class msdoc2txt
{

    public static final String CORE_DOCUMENT_REL =
	"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument";
    public static void PrintMetadata(POIFSFileSystem fs) throws IOException {
	POIDocument doc = getDocument(fs);
	SummaryInformation summary = doc.getSummaryInformation();
	prn(summary.getAuthor());
	prn(summary.getApplicationName() );
	prn(summary.getComments() );
	prn(summary.getLastAuthor() );
	prn(summary.getRevNumber() );
	prn(summary.getSubject() );
	prn(summary.getTemplate() );
	prn(summary.getTitle());
    }
    public static void prn(Object obj){
	if (obj != null){
	    System.out.println(obj);
	}
    }
    public static void PrintMetadata(OPCPackage pkg) throws IOException ,OpenXML4JException,XmlException{
	POIXMLDocument doc = getDocument(pkg);
	POIXMLProperties prop = doc.getProperties();
	CoreProperties cp = prop.getCoreProperties();
	prn(cp.getCategory() );
	prn(cp.getDescription() );
	prn(cp.getSubject());
	prn(cp.getTitle());
	prn(cp.getContentStatus() );
	prn(cp.getContentType() );
	prn(cp.getRevision() );
	prn(cp.getCreator());
    }
    public static POIXMLDocument getDocument(OPCPackage pkg) throws IOException , OpenXML4JException, XmlException {
	PackageRelationshipCollection core = 
	    pkg.getRelationshipsByType(CORE_DOCUMENT_REL);
        PackagePart corePart = pkg.getPart(core.getRelationship(0));

        if (corePart.getContentType().equals(XSSFRelation.WORKBOOK.getContentType()) ||
            corePart.getContentType().equals(XSSFRelation.MACRO_TEMPLATE_WORKBOOK.getContentType()) ||
            corePart.getContentType().equals(XSSFRelation.MACRO_ADDIN_WORKBOOK.getContentType()) ||
            corePart.getContentType().equals(XSSFRelation.TEMPLATE_WORKBOOK.getContentType()) ||
            corePart.getContentType().equals(XSSFRelation.MACROS_WORKBOOK.getContentType())) {
	    return new XSSFWorkbook(pkg);
        }

        if(corePart.getContentType().equals(XWPFRelation.DOCUMENT.getContentType()) ||
	   corePart.getContentType().equals(XWPFRelation.TEMPLATE.getContentType()) ||
	   corePart.getContentType().equals(XWPFRelation.MACRO_DOCUMENT.getContentType()) ||
	   corePart.getContentType().equals(XWPFRelation.MACRO_TEMPLATE_DOCUMENT.getContentType()) ) {
	    return new XWPFDocument(pkg);
	}
	
	if(corePart.getContentType().equals(XSLFSlideShow.MAIN_CONTENT_TYPE)) {
	    return new XSLFSlideShow(pkg);
	}

	return null;
    }
    public static POIDocument getDocument(POIFSFileSystem fs) throws IOException {
	DirectoryNode dir = fs.getRoot();
	for(Iterator entries = dir.getEntries(); entries.hasNext(); ) {
	    Entry entry = (Entry)entries.next();
	    
	    if(entry.getName().equals("Workbook")) {
		return new HSSFWorkbook(dir,fs,true);
	    }
	    if(entry.getName().equals("WordDocument")) {
		return new HWPFDocument(dir, fs);
	    }
	    if(entry.getName().equals("PowerPoint Document")) {
		return new HSLFSlideShow(dir, fs);
	    }
	    if(entry.getName().equals("VisioDocument")) {
		return new HDGFDiagram(dir, fs);
	    }
	}
	return new HSSFWorkbook(dir,fs,true);
    }

    public static void main ( String[] args )
	throws FileNotFoundException, IOException, InvalidFormatException, OpenXML4JException, XmlException
    {
	InputStream inp = System.in;
	inp = new PushbackInputStream(inp, 8);
	POITextExtractor ex ;
	if(POIFSFileSystem.hasPOIFSHeader(inp)) {
	    //System.out.println("THIS IS POIFS");
	    POIFSFileSystem fs = new POIFSFileSystem(inp);
	    PrintMetadata(fs);
	    ex = ExtractorFactory.createExtractor(fs); // hokari koko point
	}
	else if(POIXMLDocument.hasOOXMLHeader(inp)) {
	    //System.out.println("THIS IS POIXML");
	    OPCPackage pkg = OPCPackage.open(inp);
	    PrintMetadata(pkg);
	    ex = ExtractorFactory.createExtractor(pkg); // hokari koko point
	}else {
	    throw new IllegalArgumentException("Your InputStream was neither an OLE2 stream, nor an OOXML stream");
	}

	if (ex instanceof PowerPointExtractor) {
	    PowerPointExtractor powerPointExtractor =
		(PowerPointExtractor) ex;
	    prn(powerPointExtractor.getText());
	    prn(powerPointExtractor.getNotes());
	} else if (ex instanceof XSLFPowerPointExtractor) {
	    XSLFPowerPointExtractor powerPointExtractor =
		(XSLFPowerPointExtractor) ex;
	    prn(powerPointExtractor.getText());
	    prn(powerPointExtractor.getText(false, true));
	} else {
	    prn(ex.getText());
	}
    }
}