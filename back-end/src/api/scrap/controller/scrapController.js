import generateResponse from "../utils/generateResponse";

class ScrapController {
        constructor( data ) {
                this.data = data;
        }

        async change_scrap_data(req, res){
            try {
                this.data = req.body;
            }catch (error) {
                return res.status(500).json({ error: "An error occurred while updating data" });
            }
            
            const resp = await generateResponse(this.data.text);
            if (!resp) {
                return res.status(500).json({ error: "An error occurred while generating response" });
            }
            return res.status(200).json({ response: resp });


        }
}