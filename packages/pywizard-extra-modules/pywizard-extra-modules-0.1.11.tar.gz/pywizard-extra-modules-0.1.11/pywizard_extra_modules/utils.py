from pywizard.resources.shell import shell


def replace_in_file(filename, expr_from, expr_to):
    shell(
        "sed -i 's/%s/%s/g' %s" % (expr_from, expr_to, filename),
        rollback="sed -i 's/%s/%s/g' %s" % (expr_to, expr_from, filename),
    )
