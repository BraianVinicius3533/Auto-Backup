# Auto Backup - Plugin QGIS

![Logo do Plugin](icon.png)

## Descrição

O Auto Backup é um plugin para QGIS que realiza backups automáticos das camadas vetoriais em edição. Projetado para evitar a perda de dados durante sessões de edição, o plugin monitora em intervalos regulares todas as camadas que estão sendo editadas e cria cópias de segurança em um diretório de sua escolha.

## Características

- **Backup Automático**: Cria backups em intervalos definidos pelo usuário (em minutos)
- **Backup Seletivo**: Foca apenas nas camadas atualmente em modo de edição
- **Gerenciamento Inteligente**: Substitui backups antigos das mesmas camadas
- **Interface Simples**: Diálogo intuitivo para configuração e controle dos backups
- **Backups Organizados**: Cria pastas com timestamp para fácil identificação

## Instalação

### Via Gerenciador de Plugins QGIS

1. Abra o QGIS
2. Vá para "Complementos" > "Gerenciar e Instalar Complementos..."
3. Selecione a guia "Todos"
4. Pesquise por "Auto Backup"
5. Clique em "Instalar Plugin"

### Instalação Manual

1. Baixe o arquivo ZIP do plugin
2. Abra o QGIS
3. Vá para "Complementos" > "Gerenciar e Instalar Complementos..."
4. Selecione a guia "Instalar a partir do ZIP"
5. Navegue até o arquivo ZIP e clique em "Instalar Plugin"

## Como Usar

1. Clique no ícone do Auto Backup na barra de ferramentas ou acesse via menu "Complementos" > "Auto Backup"
2. Na janela de diálogo que aparece:
   - Selecione a pasta onde os backups serão salvos
   - Defina o intervalo de tempo entre backups (em minutos)
   - Clique em "Iniciar Backup Automático"
3. O plugin começará a monitorar suas camadas em edição
4. Para parar o monitoramento, clique no botão "Parar"

## Formato dos Backups

Os backups são organizados da seguinte forma:

```
pasta_selecionada/
  └── backup_QGIS-DD-MM-AAAA__HH-MM-SS/
      ├── camada1.gpkg
      ├── camada2.gpkg
      └── ...
```

Cada backup é armazenado em uma pasta separada com timestamp (data e hora), contendo arquivos GeoPackage para cada camada em edição.

## Limitações

- O plugin monitora apenas camadas vetoriais em modo de edição
- Formatos como KML, KMZ ou DWG não são incluídos no backup, a menos que estejam em modo de edição (quando permitido pelo formato)
- O plugin não faz backup de camadas raster
- É necessário que o QGIS permaneça aberto para que os backups automáticos continuem sendo realizados

## Solução de Problemas

### Nenhum backup está sendo criado

Verifique se:
- Pelo menos uma camada está em modo de edição (botão de lápis ativado)
- O intervalo de backup não é muito longo
- A pasta de destino tem permissões de escrita

### Os backups não incluem todas as camadas

Apenas camadas em modo de edição são incluídas. Para incluir uma camada no backup:
1. Selecione a camada na lista de camadas
2. Clique no botão de lápis na barra de ferramentas para iniciar a edição
3. Agora a camada será incluída nos backups automáticos

### O plugin não inicia

Verifique se:
- Você tem as permissões necessárias para executar plugins no QGIS
- A instalação do plugin foi concluída corretamente
- Não há erros no log do QGIS (Veja em "Visualizar" > "Painéis" > "Log de Mensagens")

## Requisitos

- QGIS 3.x ou superior
- Permissões de escrita no sistema de arquivos

## Suporte e Contribuições

Para relatar problemas, sugerir melhorias ou contribuir com código, acesse o repositório do projeto:
https://github.com/BraianVinicius3533/Auto-Backup

## Licença

Este plugin é distribuído sob a licença [GPL v2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html), em conformidade com o QGIS.

## Autor

Desenvolvido por [Braian Vinicius Cordeiro de Araujo]
