module.exports = {
  "testEnvironment": "jest-environment-jsdom-thirteen",
  "transform": {
    "^.+\\.js$": "babel-jest",
    "^.+\\.vue$": "vue-jest",
    "^.+\\.tsx?$": "ts-jest"
  },
  "transformIgnorePatterns": [
    "node_modules/(?!quill|parchment)"
  ]
}