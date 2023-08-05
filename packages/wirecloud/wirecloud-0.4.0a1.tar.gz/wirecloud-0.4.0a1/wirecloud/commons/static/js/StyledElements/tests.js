describe("Form Input Interfaces", function() {
    var select = null;

    afterEach(function () {
        if (select != null) {
            select.destroy();
            select = null;
        }
    });

    it("Select Input Interface", function() {
    	var select = new SelectInputInterface({
            required: false,
            initialEntries: [
                {value: 'a', label: 'first option'},
                {value: 'b', label: 'second option'},
                {value: 'c', label: 'third option'}
            ]
        });

	var values = Array.prototype.slice.call(document.getElementsByTagName('select')[3].options).map(function (element) { return element.getAttribute('value') });

	expect(options).toBe(['', 'a', 'b', 'c']);

        var labels = Array.prototype.slice.call(document.getElementsByTagName('select')[3].options).map(function (element) { return element.getAttribute('label') });

        expect(labels).toBe(['---------', 'first option', 'second option', 'third option']);
    });

    it("Required Select Input Interface", function() {
    	var select = new SelectInputInterface({
            required: true,
            initialEntries: [
                {value: 'a', label: 'first option'},
                {value: 'b', label: 'second option'},
                {value: 'c', label: 'third option'}
            ]
        });

	var values = Array.prototype.slice.call(document.getElementsByTagName('select')[3].options).map(function (element) { return element.getAttribute('value') });

	expect(options).toBe(['a', 'b', 'c']);

        var labels = Array.prototype.slice.call(document.getElementsByTagName('select')[3].options).map(function (element) { return element.getAttribute('label') });

        expect(labels).toBe(['first option', 'second option', 'third option']);
    });

});
