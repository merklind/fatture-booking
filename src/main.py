from pathlib import Path

from pymupdf import open

from argparser_config import setup_parser
from logger_config import setup_logger
from utils.path import find_all_files

_STRING_TO_REPLACE = [
    'Suite Fiera Milano City',
    'Individual entrepreneur Patrizio Melis',
    'Residenza Porta Romana',
    'Individual entrepreneur Walter Melis',
]
_ASCENDER = 2.6369934082

if __name__ == '__main__':
    logger = setup_logger(name=__name__)
    parsed_arg = setup_parser()

    logger.info(f"Scanning folder: {parsed_arg.filename}")

    Path("output").mkdir(parents=True, exist_ok=True)

    asset_folder = Path(parsed_arg.filename)

    invoice_to_compute = find_all_files(asset_folder)

    logger.info(f"Found {len(invoice_to_compute)} files")

    for file in invoice_to_compute:
        folder_name = file.parts[-2]
        filename = file.name

        doc = open(file)

        page = doc.load_page(0)

        for to_replace in _STRING_TO_REPLACE:
            search_results = page.search_for(to_replace)

            if len(search_results) > 1:
                raise ValueError(f"Too much text matching in file {folder_name} - {filename}.\n"
                                 f"Found {len(search_results)} matches")

            if len(search_results) == 1:
                [result] = search_results

                x0 = result.x0
                y1 = result.y1 - _ASCENDER

                page.add_redact_annot(result, fill=(1, 1, 1))
                page.apply_redactions()

                page.insert_font(fontname="F0", fontfile="asset/NotoSans-Regular.ttf")

                page.insert_text((x0, y1), "SAHI s.r.l.s", fontsize=9, fontname="F0", color=(0.2, 0.2, 0.2))

        logger.info(f"Processing file ${folder_name}/{filename} completed")

        doc.save(f"output/{folder_name}-{filename}")
        doc.close()
