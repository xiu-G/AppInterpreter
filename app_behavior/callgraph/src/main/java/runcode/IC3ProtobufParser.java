package runcode;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import com.google.protobuf.TextFormat;

import edu.psu.cse.siis.ic3.Ic3Data;
import edu.psu.cse.siis.ic3.Ic3Data.Application.Component;
import edu.psu.cse.siis.ic3.Ic3Data.Application.Component.ComponentKind;
import edu.psu.cse.siis.ic3.Ic3Data.Application.Component.ExitPoint;
import edu.psu.cse.siis.ic3.Ic3Data.Application.Component.Extra;
import edu.psu.cse.siis.ic3.Ic3Data.Application.Component.ExitPoint.Intent;
import edu.psu.cse.siis.ic3.Ic3Data.Application.Component.ExitPoint.Uri;
import edu.psu.cse.siis.ic3.Ic3Data.Attribute;
import edu.psu.cse.siis.ic3.Ic3Data.AttributeKind;

public class IC3ProtobufParser {
	Ic3Data.Application.Builder ic3Builder;
	HashMap<String, ArrayList<String>> iccs = new HashMap<>();

	public HashMap<String, ArrayList<String>> parseFromFile(String filename)
			throws FileNotFoundException, IOException {
		ic3Builder = Ic3Data.Application.newBuilder();
		TextFormat.merge(new FileReader(new File(filename)), ic3Builder);

		System.out.println(ic3Builder.toString());

		List<Component> componentsList = ic3Builder.getComponentsList();
		for (Component component : componentsList) {
			// System.out.println("========= " + component.getName() + "
			// =========");
			List<ExitPoint> exitpoints = component.getExitPointsList();
			List<Extra> extras = component.getExtrasList();
			for (ExitPoint exitPoint : exitpoints) {
				String fromMethod = exitPoint.getInstruction().getMethod();	
				List<Intent> intentsList = exitPoint.getIntentsList();
				HashSet<String> providerUristrings = new HashSet<String>();
				if (!iccs.containsKey(fromMethod)) {
					iccs.put(fromMethod, new ArrayList<String>());
				}
				if (exitPoint.getKind() == ComponentKind.PROVIDER) {
					List<Uri> urisList = exitPoint.getUrisList();
					for (Uri uri : urisList) {
						for (Attribute attribute : uri.getAttributesList()) {
							if (attribute.getKind() == AttributeKind.URI) {
								providerUristrings.add("providerUristrings###"+attribute.getValue(0));
							}
						}
					}
				}
				for (Intent intent : intentsList) {
					List<Attribute> attributesList = intent.getAttributesList();
					String toClass="", action="", type="", uri="", scheme = "";

					for (Attribute attribute : attributesList) {
						if (attribute.getKind() == AttributeKind.CLASS) {
							toClass = "toclass###"+attribute.getValue(0).replace("/", ".");
						}
						else if (attribute.getKind() == AttributeKind.ACTION) {
							action = attribute.getValue(0);
						}
						else if (attribute.getKind() == AttributeKind.TYPE) {
							type = attribute.getValue(0);
						}
						else if (attribute.getKind() == AttributeKind.URI) {
							uri = attribute.getValue(0);
						}
						else if (attribute.getKind() == AttributeKind.SCHEME) {
							scheme = attribute.getValue(0);
						}
					}
					if (!toClass.equals("") && !toClass.startsWith("(") && !iccs.get(fromMethod).contains(toClass)){
						iccs.get(fromMethod).add(toClass);
					}else{
						if (action.equals("") || action.startsWith("<") || action.startsWith("(")){
							continue;
						}else{
							action = "actions###"+action;
							if (!scheme.equals("") && !scheme.startsWith("<") && !scheme.startsWith("(")){
								action = action+"###schemes###"+scheme;
							}
							if (!type.equals("") && !type.startsWith("<") && !type.startsWith("(")){
								action = action+"###types###"+type;
							}
							if (!uri.equals("") && !uri.startsWith("<") && !uri.startsWith("(")){
								action = action+"###uri###"+uri;
							}
							if (!iccs.get(fromMethod).contains(action)){
								iccs.get(fromMethod).add(action);
							}
						}
						
					}	
					iccs.get(fromMethod).addAll(providerUristrings);
				}
				
			}
			
			for (Extra extra : extras) {
				String fromMethod = extra.getInstruction().getMethod();	
				String extraString = "extra###"+extra.getExtra();
				if (!iccs.containsKey(fromMethod)) {
					iccs.put(fromMethod, new ArrayList<String>());
				}
				iccs.get(fromMethod).add(extraString);
			}
		}
		System.out.println("read successfully");
		return iccs;
	}

}
