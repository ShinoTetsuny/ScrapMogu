import generateResponse from "../src/api/scrap/utils/generateResponse.js";
import { describe, expect } from "@jest/globals";

describe("check the response from openai", () => {
  it("should return a response from Openai", async () => {
  await generateResponse("hello").then(res => {
    expect(res).toBeDefined();
    expect(typeof res).toBe("string");
  });
}, 10000);
});
