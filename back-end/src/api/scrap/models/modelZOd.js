import { z } from "zod";

export const characterSchema = z.object({
  nom: z.string().min(1, "Le nom est requis"),
  image: z.string().url("L'image doit être une URL valide"),
  description: z.string().min(1, "La description est requise"),
  role: z.string().min(1, "Le rôle est requis"),
  origine: z.string().min(1, "L'origine est requise"),
  attributs: z.record(z.string().min(1)) // clé: valeur, avec valeur string non vide
});


export default characterSchema;