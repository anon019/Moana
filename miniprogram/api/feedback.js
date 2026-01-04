"use strict";const e=require("./request.js");exports.submitFeedback=async function(s){return e.request.post("/feedback",s)};
