#!/bin/bash 

i18ndude rebuild-pot --pot faq.pot --create faqulator ../
i18ndude sync --pot faq.pot faq-*.po 

