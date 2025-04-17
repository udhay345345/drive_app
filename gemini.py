from google import genai
from google.genai import types
import pathlib
import httpx


client = genai.Client(api_key="AIzaSyCkLJR2Or2JG-4nRZk9spI34_RyOUI-V68")

doc_url = "https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf"  # Replace with the actual URL of your PDF

# Retrieve and encode the PDF byte
filepath = pathlib.Path('English_textbook.pdf')
# filepath.write_bytes(httpx.get(doc_url).content)

prompt = f"""
            Task : Generate 15 to 20 questions from the data provided to you
            Instructions:
                1. Questions should be only from that data 
                2. They should be very straight forward 
                3. They should be neither very easy nor very hard
                4. Questions should cover the entire content especially main points
          """
response = client.models.generate_content(
  model="gemini-2.0-flash",
  contents=[
      types.Part.from_bytes(
        data=filepath.read_bytes(),
        mime_type='application/pdf',
      ),
      prompt])
print(response.text)
