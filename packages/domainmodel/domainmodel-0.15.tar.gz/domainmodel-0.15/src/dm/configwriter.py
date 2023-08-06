import re

# Todo: Rename ConfigWriter as ConfigMerger.
class ConfigWriter(object):

    def updateLines(self, configLines, updateLines):
        configDoc = ConfigDoc(configLines)
        updateDoc = ConfigDoc(updateLines)
        configDoc.update(updateDoc)
        self.newLines = configDoc.asLines()

    def updateFile(self, configPath, updateLines):
        configFile = open(configPath, 'r')
        configLines = configFile.readlines()
        configFile.close()
        self.updateLines(configLines, updateLines)
        configFile = open(configPath, 'w')
        configLines = configFile.writelines(configLines)
        configFile.close()


class ConfigDoc(object):

    def __init__(self, lines):
        reSection = re.compile('^\[\w+\]')
        self.sections = []
        self.prelines = []
        section = None
        for line in lines:
            if line[-1:] == '\n':
                line = line[:-1]
            match = reSection.match(line)
            if match:
                if section and section.lines:
                    lastLine = section.lines[-1]
                    if lastLine.name == '' and lastLine.comment == '':
                        section.lines.pop()
                sectionName = match.group()[1:-1]
                section = ConfigSection(sectionName)
                self.sections.append(section)
            elif section:
                section.parseLine(line)
            else:
                self.prelines.append(line.strip())

    def update(self, configDoc):
        sectionDict = {}
        for section in self.sections:
            sectionDict[section.name] = section
        for section in configDoc.sections:
            if section.name in sectionDict:
                sectionDict[section.name].update(section)
            else:
                self.sections.append(section)

    def asLines(self):
        lines = []
        for section in self.sections:
            lines += section.asLines()
            lines.append('')
        self.sections and lines.pop()
        lines = self.prelines + lines
        lines = [l+'\n' for l in lines]
        return lines
        

class ConfigSection(object):

    def __init__(self, name):
        self.name = name
        self.lines = []

    def parseLine(self, line):
        self.lines.append(ConfigLine(line))

    def update(self, configSection):
        lineDict = {}
        for line in self.lines:
            if line.name:
                lineDict[line.name] = line
        for line in configSection.lines:
            if line.name in lineDict:
                lineDict[line.name].update(line)
            else:
                self.lines.append(line)

    def asLines(self):
        lines = []
        lines.append('[%s]' % self.name)
        for line in self.lines:
            lines.append(line.asText())
        return lines


class ConfigLine(object):

    def __init__(self, line):
        self.isCommentedOut = False
        self.hasComment = False
        self.hasAssignment = False
        self.name = ''
        self.value = ''
        self.comment = ''
        self.parseLine(line)

    def parseLine(self, line):
        if line and line[0] == '#':
            self.isCommentedOut = True
            line = line[1:]
        if '#' in line:
            self.hasComment = True
            lineSplit = line.split('#', 1)
            self.comment = lineSplit[1]
            self.chaff = lineSplit[0]
        else:
            self.chaff = line
        if '=' in self.chaff and ' ' not in self.chaff.split('=')[0].strip():
            self.hasAssignment = True
            chaffSplit = self.chaff.split('=', 1)
            self.name = chaffSplit[0].strip()
            self.value = chaffSplit[1].strip()

    def update(self, configLine):
        self.value = configLine.value
        self.isCommentedOut = False

    def asText(self):
        if self.hasAssignment:
            text = '%s = %s' % (self.name, self.value)
        else:
            text = self.chaff
        if self.hasComment:
            text = '%s #%s' % (text, self.comment)
        if self.isCommentedOut:
            text = '#%s' % text
        return text
