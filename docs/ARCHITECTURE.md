# Arquitetura do MDForge

## Fluxo

`GUI/CLI -> ConversionService -> ConverterRegistry -> Converter -> Markdown`

## Princípios

- Separação entre domínio de conversão e interfaces.
- Um conversor por responsabilidade/formato.
- Registro central simples, substituível por descoberta dinâmica no futuro.
- Falhas retornam `ConversionResult`; a camada de UI decide como exibi-las.

## Evolução

Para uma versão maior, considere:

- `Protocol`/entry points para plugins externos.
- Fila de jobs e threads para não bloquear a UI.
- Modelo intermediário de documento (AST) para preservar semântica entre formatos.
- Pipeline configurável de limpeza/normalização Markdown.
- Telemetria apenas opt-in e nunca contendo conteúdo dos documentos.
