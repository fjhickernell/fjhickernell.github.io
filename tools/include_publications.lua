-- Read the generated catalog after pre-render, rather than during Quarto's
-- project discovery, when a fresh checkout has no generated include yet.
function Div(el)
  if el.identifier ~= "generated-publications" then
    return nil
  end
  local path = quarto.project.directory .. "/_includes/publications.html"
  local file, err = io.open(path, "r")
  if not file then
    error("Cannot read generated publications catalog: " .. tostring(err))
  end
  local content = file:read("*a")
  file:close()
  return pandoc.read(content, "markdown").blocks
end
